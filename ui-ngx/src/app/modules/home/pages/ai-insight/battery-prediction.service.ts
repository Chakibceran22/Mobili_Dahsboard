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

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface BatteryPredictionResponse {
  original_battery_data: number[];
  input_sequence_used: number[];
  predicted_sequence: number[];
  actual_sequence: number[];
  prediction_cycles: number[];
  info: {
    total_test_samples: number;
    sample_shown: number;
    input_length: number;
    prediction_length: number;
    max_cycle_limit: number;
    predictions_before_filtering: number;
    predictions_after_filtering: number;
    methodology: string;
  };
}

export interface BatteryHealthStatus {
  status: string;
  model_loaded: boolean;
  test_data_loaded: boolean;
  timestamp: string;
}

export interface BatteryDataPoint {
  cycle: number;
  capacity: number;
  type: 'input' | 'predicted' | 'actual';
}

@Injectable({
  providedIn: 'root'
})
export class BatteryPredictionService {
  private baseUrl = 'http://192.168.0.1:5010';

  constructor(private http: HttpClient) { }

  getBatteryPrediction(): Observable<BatteryPredictionResponse> {
    return this.http.get<BatteryPredictionResponse>(`${this.baseUrl}/predict`);
  }

  getBatteryHealthStatus(): Observable<BatteryHealthStatus> {
    return this.http.get<BatteryHealthStatus>(`${this.baseUrl}/health`);
  }

  processBatteryData(data: BatteryPredictionResponse): BatteryDataPoint[] {
    const points: BatteryDataPoint[] = [];
    
    // Add input sequence points
    data.input_sequence_used.forEach((capacity, index) => {
      points.push({
        cycle: index + 1,
        capacity: capacity,
        type: 'input'
      });
    });
    
    // Add predicted points
    data.predicted_sequence.forEach((capacity, index) => {
      points.push({
        cycle: data.prediction_cycles[index],
        capacity: capacity,
        type: 'predicted'
      });
    });
    
    // Add actual points (for comparison)
    data.actual_sequence.forEach((capacity, index) => {
      if (index < data.prediction_cycles.length) {
        points.push({
          cycle: data.prediction_cycles[index],
          capacity: capacity,
          type: 'actual'
        });
      }
    });
    
    return points.sort((a, b) => a.cycle - b.cycle);
  }

  calculatePredictionMetrics(data: BatteryPredictionResponse): {
    remainingUsefulLife: number;
    degradationRate: number;
    healthPercentage: number;
    endOfLifeCycle: number;
  } {
    const { predicted_sequence, prediction_cycles, input_sequence_used } = data;
    
    // Calculate degradation rate (capacity loss per cycle)
    const initialCapacity = input_sequence_used[0];
    const currentCapacity = input_sequence_used[input_sequence_used.length - 1];
    const currentCycle = input_sequence_used.length;
    
    const degradationRate = (initialCapacity - currentCapacity) / currentCycle;
    
    // Health percentage based on current capacity vs initial
    const healthPercentage = (currentCapacity / initialCapacity) * 100;
    
    // Find when battery reaches 80% of initial capacity (common EOL threshold)
    const eolThreshold = initialCapacity * 0.8;
    
    // Look for when predicted capacity drops below threshold
    let endOfLifeCycle = 0;
    for (let i = 0; i < predicted_sequence.length; i++) {
      if (predicted_sequence[i] <= eolThreshold) {
        endOfLifeCycle = prediction_cycles[i];
        break;
      }
    }
    
    // If not found in predictions, extrapolate
    if (endOfLifeCycle === 0) {
      const lastPredictedCycle = prediction_cycles[prediction_cycles.length - 1];
      const lastPredictedCapacity = predicted_sequence[predicted_sequence.length - 1];
      
      if (degradationRate > 0) {
        const cyclesRemaining = (lastPredictedCapacity - eolThreshold) / degradationRate;
        endOfLifeCycle = lastPredictedCycle + cyclesRemaining;
      }
    }
    
    const remainingUsefulLife = Math.max(0, endOfLifeCycle - currentCycle);
    
    return {
      remainingUsefulLife: Math.round(remainingUsefulLife),
      degradationRate: Number(degradationRate.toFixed(6)),
      healthPercentage: Number(healthPercentage.toFixed(1)),
      endOfLifeCycle: Math.round(endOfLifeCycle)
    };
  }
}
