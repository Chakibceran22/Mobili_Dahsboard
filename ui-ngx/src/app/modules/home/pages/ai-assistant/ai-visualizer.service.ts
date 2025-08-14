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
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface VisualizationRequest {
  prompt: string;
}

export interface VisualizationResponse {
  success: boolean;
  message?: string;
  plot_url?: string;
  error?: string;
  details?: {
    device_selected?: string;
    parameters_extracted?: any;
    smart_selector_info?: any;
  };
}

export interface VisualizationMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
  plotUrl?: string;
  details?: any;
}

@Injectable({
  providedIn: 'root'
})
export class AiVisualizerService {
  private readonly API_BASE_URL = 'http://192.168.0.101:8003';

  constructor(private http: HttpClient) {}

  sendVisualizationRequest(prompt: string): Observable<VisualizationResponse> {
    const request: VisualizationRequest = { prompt };

    return this.http.post<VisualizationResponse>(`${this.API_BASE_URL}/chat`, request)
      .pipe(
        catchError(this.handleError)
      );
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Error ${error.status}: ${error.message}`;
      if (error.error?.error) {
        errorMessage = error.error.error;
      }
    }

    console.error('Visualization service error:', error);
    return throwError(errorMessage);
  }
}