///
/// Copyright © 2016-2025 The Thingsboard Authors
///
/// Licensed under the Apache License, Version 2.0 (the "License");
/// you may not use this file except in compliance with the License.
/// You may obtain a copy of the License at
///
///     http://www.apache.org/licenses/LICENSE-2.0
///
/// Unless required by applicable law or agreed to in writing, software
/// distributed under the License is distributed on an "AS IS" BASIS,
/// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
/// See the License for the specific language governing permissions and
/// limitations under the License.
///

import { Component, OnInit, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { TimeseriesService, DataPoint } from './timeseries.service';
import { BatteryPredictionService, BatteryDataPoint, BatteryPredictionResponse, BatteryHealthStatus } from './battery-prediction.service';
import { trigger, state, style, transition, animate } from '@angular/animations';
import * as d3 from 'd3';

@Component({
  selector: 'tb-ai-insight',
  templateUrl: './ai-insight.component.html',
  styleUrls: ['./ai-insight.component.scss'],
  animations: [
    trigger('slideDown', [
      transition(':enter', [
        style({ height: '0px', opacity: 0, overflow: 'hidden' }),
        animate('300ms ease-in-out', style({ height: '*', opacity: 1 }))
      ]),
      transition(':leave', [
        style({ height: '*', opacity: 1, overflow: 'hidden' }),
        animate('300ms ease-in-out', style({ height: '0px', opacity: 0 }))
      ])
    ])
  ]
})
export class AiInsightComponent implements OnInit, AfterViewInit {
  @ViewChild('timeseriesChart', { static: false }) chartContainer: ElementRef;
  @ViewChild('batteryChart', { static: false }) batteryChartContainer: ElementRef;

  // Timeseries properties
  timeSeriesData: DataPoint[] = [];
  loading = false;
  error: string | null = null;
  anomalyCount = 0;
  totalPoints = 0;
  modelType = '';
  anomalyPercentage = 0;
  
  // Timeseries settings
  showPredictions = true;
  showAnomalyPoints = true;
  showSettings = false;

  // Battery prediction properties
  batteryData: BatteryDataPoint[] = [];
  batteryPredictionResponse: BatteryPredictionResponse | null = null;
  batteryHealthStatus: BatteryHealthStatus | null = null;
  batteryMetrics: any = null;
  batteryLoading = false;
  batteryError: string | null = null;

  // Battery settings
  showInputSequence = true;
  showActualValues = true;
  showEOLLine = true;
  showBatterySettings = false;

  constructor(
    private timeseriesService: TimeseriesService,
    private batteryPredictionService: BatteryPredictionService
  ) { }

  ngOnInit(): void {
  }

  ngAfterViewInit(): void {
    this.loadTimeSeriesData();
    this.loadBatteryPredictionData();
  }

  loadTimeSeriesData(): void {
    this.loading = true;
    this.error = null;

    this.timeseriesService.getTimeSeriesData().subscribe({
      next: (response) => {
        this.timeSeriesData = this.timeseriesService.processTimeSeriesData(response.data);
        this.anomalyCount = response.data.metadata.anomaly_count;
        this.totalPoints = response.data.metadata.total_points;
        this.modelType = response.data.metadata.model_type;
        this.anomalyPercentage = response.data.metadata.anomaly_percentage;
        this.loading = false;
        
        // Wait for DOM update then create chart
        setTimeout(() => {
          this.createChart();
        }, 100);
      },
      error: (error) => {
        this.error = 'Failed to load time series data. Make sure the Flask API is running on port 5002.';
        this.loading = false;
        console.error('Time series API error:', error);
      }
    });
  }

  private createChart(): void {
    if (!this.chartContainer || this.timeSeriesData.length === 0) {
      return;
    }

    // Clear any existing chart
    d3.select(this.chartContainer.nativeElement).selectAll('*').remove();

    const container = this.chartContainer.nativeElement;
    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Set up scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(this.timeSeriesData, d => d.timestamp))
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(d3.extent([
        ...this.timeSeriesData.map(d => d.value),
        ...this.timeSeriesData.map(d => d.prediction)
      ]))
      .nice()
      .range([height, 0]);

    // Create line generators
    const groundTruthLine = d3.line<DataPoint>()
      .x(d => xScale(d.timestamp))
      .y(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    const predictionLine = d3.line<DataPoint>()
      .x(d => xScale(d.timestamp))
      .y(d => yScale(d.prediction))
      .curve(d3.curveMonotoneX);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%H:%M')));

    g.append('g')
      .call(d3.axisLeft(yScale));

    // Add axis labels
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Solar Power (kW)');

    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom})`)
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Time');

    // Add the ground truth line
    g.append('path')
      .datum(this.timeSeriesData)
      .attr('fill', 'none')
      .attr('stroke', '#4CAF50')
      .attr('stroke-width', 2)
      .attr('d', groundTruthLine);

    // Add the prediction line (conditionally)
    if (this.showPredictions) {
      g.append('path')
        .datum(this.timeSeriesData)
        .attr('fill', 'none')
        .attr('stroke', '#2196F3')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('d', predictionLine);
    }

    // Add legend
    const legend = g.append('g')
      .attr('transform', `translate(${width - 120}, 20)`);

    legend.append('line')
      .attr('x1', 0)
      .attr('x2', 20)
      .attr('y1', 0)
      .attr('y2', 0)
      .attr('stroke', '#4CAF50')
      .attr('stroke-width', 2);

    legend.append('text')
      .attr('x', 25)
      .attr('y', 5)
      .style('font-size', '12px')
      .text('Ground Truth');

    if (this.showPredictions) {
      legend.append('line')
        .attr('x1', 0)
        .attr('x2', 20)
        .attr('y1', 15)
        .attr('y2', 15)
        .attr('stroke', '#2196F3')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5');

      legend.append('text')
        .attr('x', 25)
        .attr('y', 20)
        .style('font-size', '12px')
        .text('Prediction');
    }

    // Add normal points (on ground truth line)
    g.selectAll('.normal-point')
      .data(this.timeSeriesData.filter(d => !d.isAnomaly))
      .enter().append('circle')
      .attr('class', 'normal-point')
      .attr('cx', d => xScale(d.timestamp))
      .attr('cy', d => yScale(d.value))
      .attr('r', 3)
      .attr('fill', '#4CAF50')
      .attr('opacity', 0.7);

    // Add anomaly points (conditionally, highlighted on ground truth line)
    if (this.showAnomalyPoints) {
      g.selectAll('.anomaly-point')
        .data(this.timeSeriesData.filter(d => d.isAnomaly))
        .enter().append('circle')
        .attr('class', 'anomaly-point')
        .attr('cx', d => xScale(d.timestamp))
        .attr('cy', d => yScale(d.value))
        .attr('r', 5)
        .attr('fill', '#f44336')
        .attr('stroke', '#d32f2f')
        .attr('stroke-width', 2);
    }

    // Add tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0)
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('padding', '8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('pointer-events', 'none');

    // Add hover effects
    g.selectAll('circle')
      .on('mouseover', function(event: any, d: DataPoint) {
        tooltip.transition().duration(200).style('opacity', .9);
        tooltip.html(`
          <strong>${d.isAnomaly ? 'ANOMALY DETECTED' : 'Normal Point'}</strong><br/>
          Time: ${d.timestamp.toLocaleTimeString()}<br/>
          Ground Truth: ${d.value.toFixed(2)} kW<br/>
          Prediction: ${d.prediction.toFixed(2)} kW<br/>
          Anomaly Score: ${d.anomaly_score.toFixed(4)}<br/>
          Difference: ${Math.abs(d.value - d.prediction).toFixed(2)} kW
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        tooltip.transition().duration(500).style('opacity', 0);
      });
  }

  refreshData(): void {
    this.loadTimeSeriesData();
  }

  toggleSettings(): void {
    this.showSettings = !this.showSettings;
  }

  onSettingsChange(): void {
    // Recreate chart when settings change
    if (this.timeSeriesData.length > 0) {
      setTimeout(() => {
        this.createChart();
      }, 50);
    }
  }

  // Battery Prediction Methods
  loadBatteryPredictionData(): void {
    this.batteryLoading = true;
    this.batteryError = null;

    // First check health status
    this.batteryPredictionService.getBatteryHealthStatus().subscribe({
      next: (status) => {
        this.batteryHealthStatus = status;
        
        // If model is ready, get prediction data
        if (status.model_loaded && status.test_data_loaded) {
          this.batteryPredictionService.getBatteryPrediction().subscribe({
            next: (response) => {
              this.batteryPredictionResponse = response;
              this.batteryData = this.batteryPredictionService.processBatteryData(response);
              this.batteryMetrics = this.batteryPredictionService.calculatePredictionMetrics(response);
              this.batteryLoading = false;
              
              // Wait for DOM update then create chart
              setTimeout(() => {
                this.createBatteryChart();
              }, 100);
            },
            error: (error) => {
              this.batteryError = 'Failed to load battery prediction data. Make sure the Flask API is running on port 5010.';
              this.batteryLoading = false;
              console.error('Battery prediction API error:', error);
            }
          });
        } else {
          this.batteryError = 'Battery prediction model is not ready. Please check the API health status.';
          this.batteryLoading = false;
        }
      },
      error: (error) => {
        this.batteryError = 'Failed to check battery prediction service health. Make sure the Flask API is running on port 5010.';
        this.batteryLoading = false;
        console.error('Battery health API error:', error);
      }
    });
  }

  private createBatteryChart(): void {
    if (!this.batteryChartContainer || this.batteryData.length === 0) {
      return;
    }

    // Clear any existing chart
    d3.select(this.batteryChartContainer.nativeElement).selectAll('*').remove();

    const container = this.batteryChartContainer.nativeElement;
    const margin = { top: 20, right: 30, bottom: 60, left: 60 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Separate data by type
    const inputData = this.batteryData.filter(d => d.type === 'input');
    const predictedData = this.batteryData.filter(d => d.type === 'predicted');
    const actualData = this.batteryData.filter(d => d.type === 'actual');

    // Set up scales
    const xScale = d3.scaleLinear()
      .domain(d3.extent(this.batteryData, d => d.cycle))
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(d3.extent(this.batteryData, d => d.capacity))
      .nice()
      .range([height, 0]);

    // Create line generators
    const inputLine = d3.line<BatteryDataPoint>()
      .x(d => xScale(d.cycle))
      .y(d => yScale(d.capacity))
      .curve(d3.curveMonotoneX);

    const predictionLine = d3.line<BatteryDataPoint>()
      .x(d => xScale(d.cycle))
      .y(d => yScale(d.capacity))
      .curve(d3.curveMonotoneX);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.format('d')));

    g.append('g')
      .call(d3.axisLeft(yScale));

    // Add axis labels
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Battery Capacity (Ah)');

    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 10})`)
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Charge Cycle');

    // Add End-of-Life threshold line (80% of initial capacity)
    if (this.showEOLLine && this.batteryPredictionResponse) {
      const initialCapacity = this.batteryPredictionResponse.input_sequence_used[0];
      const eolThreshold = initialCapacity * 0.8;
      
      g.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', yScale(eolThreshold))
        .attr('y2', yScale(eolThreshold))
        .attr('stroke', '#ff5722')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '10,5')
        .attr('opacity', 0.7);

      g.append('text')
        .attr('x', width - 100)
        .attr('y', yScale(eolThreshold) - 5)
        .style('font-size', '10px')
        .style('fill', '#ff5722')
        .text('End-of-Life (80%)');
    }

    // Add the input sequence line
    if (this.showInputSequence && inputData.length > 0) {
      g.append('path')
        .datum(inputData)
        .attr('fill', 'none')
        .attr('stroke', '#4CAF50')
        .attr('stroke-width', 2)
        .attr('d', inputLine);

      // Add input points
      g.selectAll('.input-point')
        .data(inputData)
        .enter().append('circle')
        .attr('class', 'input-point')
        .attr('cx', d => xScale(d.cycle))
        .attr('cy', d => yScale(d.capacity))
        .attr('r', 2)
        .attr('fill', '#4CAF50');
    }

    // Add the prediction line
    if (predictedData.length > 0) {
      g.append('path')
        .datum(predictedData)
        .attr('fill', 'none')
        .attr('stroke', '#2196F3')
        .attr('stroke-width', 3)
        .attr('stroke-dasharray', '5,5')
        .attr('d', predictionLine);

      // Add prediction points
      g.selectAll('.prediction-point')
        .data(predictedData)
        .enter().append('circle')
        .attr('class', 'prediction-point')
        .attr('cx', d => xScale(d.cycle))
        .attr('cy', d => yScale(d.capacity))
        .attr('r', 3)
        .attr('fill', '#2196F3')
        .attr('stroke', '#1976D2')
        .attr('stroke-width', 1);
    }

    // Add actual values for comparison
    if (this.showActualValues && actualData.length > 0) {
      g.selectAll('.actual-point')
        .data(actualData)
        .enter().append('circle')
        .attr('class', 'actual-point')
        .attr('cx', d => xScale(d.cycle))
        .attr('cy', d => yScale(d.capacity))
        .attr('r', 3)
        .attr('fill', '#FF9800')
        .attr('stroke', '#F57C00')
        .attr('stroke-width', 2);
    }

    // Add tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'battery-tooltip')
      .style('opacity', 0)
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('padding', '8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('pointer-events', 'none');

    // Add hover effects
    g.selectAll('circle')
      .on('mouseover', function(event: any, d: BatteryDataPoint) {
        tooltip.transition().duration(200).style('opacity', .9);
        tooltip.html(`
          <strong>${d.type.toUpperCase()}</strong><br/>
          Cycle: ${d.cycle}<br/>
          Capacity: ${d.capacity.toFixed(3)} Ah<br/>
          Type: ${d.type === 'input' ? 'Historical Data' : 
                 d.type === 'predicted' ? 'LSTM Prediction' : 'Actual Value'}
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        tooltip.transition().duration(500).style('opacity', 0);
      });
  }

  refreshBatteryData(): void {
    this.loadBatteryPredictionData();
  }

  toggleBatterySettings(): void {
    this.showBatterySettings = !this.showBatterySettings;
  }

  onBatterySettingsChange(): void {
    // Recreate chart when settings change
    if (this.batteryData.length > 0) {
      setTimeout(() => {
        this.createBatteryChart();
      }, 50);
    }
  }

  getHealthColor(healthPercentage: number): string {
    if (healthPercentage >= 90) return '#4CAF50'; // Green
    if (healthPercentage >= 80) return '#FF9800'; // Orange
    if (healthPercentage >= 70) return '#FF5722'; // Red-Orange
    return '#f44336'; // Red
  }
}
