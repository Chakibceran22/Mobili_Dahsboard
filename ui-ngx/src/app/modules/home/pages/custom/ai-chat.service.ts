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
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface ChatMessage {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: string;
  sources?: Source[];
}

export interface Source {
  title: string;
  category: string;
  url?: string;
}

export interface ChatResponse {
  response: string;
  timestamp: string;
  sources: Source[];
}

export interface DatabaseStatus {
  connected: boolean;
  document_count?: number;
}

@Injectable({
  providedIn: 'root'
})
export class AiChatService {
  private readonly API_BASE_URL = 'http://localhost:8001';

  constructor(private http: HttpClient) { }

  sendMessage(message: string, apiKey: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.API_BASE_URL}/chat`, {
      message,
      api_key: apiKey
    }).pipe(
      catchError(this.handleError)
    );
  }

  getDatabaseStatus(): Observable<DatabaseStatus> {
    return this.http.get<DatabaseStatus>(`${this.API_BASE_URL}/status`).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: any): Observable<never> {
    let errorMessage = 'An unexpected error occurred';
    
    if (error.error?.detail) {
      errorMessage = error.error.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    return throwError(() => new Error(errorMessage));
  }
}
