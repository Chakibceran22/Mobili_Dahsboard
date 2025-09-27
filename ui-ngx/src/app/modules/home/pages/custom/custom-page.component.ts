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

import { Component, OnInit, AfterViewChecked, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { AiChatService, ChatMessage, DatabaseStatus } from './ai-chat.service';
import { Subject, interval } from 'rxjs';
import { takeUntil, switchMap } from 'rxjs/operators';

@Component({
  selector: 'tb-custom-page',
  templateUrl: './custom-page.component.html',
  styleUrls: ['./custom-page.component.scss']
})
export class CustomPageComponent implements OnInit, AfterViewChecked, OnDestroy {
  @ViewChild('messagesContainer') private messagesContainer: ElementRef;
  @ViewChild('messageInput') private messageInput: ElementRef;

  messages: ChatMessage[] = [];
  inputValue = '';
  apiKey = '';
  showSettings = false;
  loading = false;
  error: string | null = null;
  dbStatus: DatabaseStatus | null = null;

  private destroy$ = new Subject<void>();
  private shouldScrollToBottom = false;

  sampleQuestions = [
    "How do I connect a device to ThingsBoard?",
    "What is device provisioning?",
    "How to use MQTT with ThingsBoard?",
    "How to create a dashboard?"
  ];

  constructor(private aiChatService: AiChatService) {
    // Load API key from localStorage
    this.apiKey = localStorage.getItem('gemini_api_key') || '';
  }

  ngOnInit(): void {
    this.loadDatabaseStatus();
    // Poll database status every 30 seconds
    interval(30000)
      .pipe(
        takeUntil(this.destroy$),
        switchMap(() => {
          console.log('Polling database status...');
          return this.aiChatService.getDatabaseStatus();
        })
      )
      .subscribe({
        next: (status) => {
          console.log('Polled database status received:', status);
          this.dbStatus = status;
        },
        error: (err) => {
          console.error('Failed to poll database status:', err);
          // Set status to disconnected on error
          this.dbStatus = { connected: false };
        }
      });
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadDatabaseStatus(): void {
    console.log('Loading database status...');
    this.aiChatService.getDatabaseStatus()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (status) => {
          console.log('Database status received:', status);
          this.dbStatus = status;
        },
        error: (err) => {
          console.error('Failed to load database status:', err);
          // Set status to disconnected on error
          this.dbStatus = { connected: false };
        }
      });
  }

  sendMessage(): void {
    if (!this.inputValue.trim() || !this.apiKey.trim() || this.loading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: Date.now(),
      text: this.inputValue,
      isUser: true,
      timestamp: new Date().toISOString()
    };

    this.messages.push(userMessage);
    this.shouldScrollToBottom = true;
    
    const messageText = this.inputValue;
    this.inputValue = '';
    this.loading = true;
    this.error = null;

    this.aiChatService.sendMessage(messageText, this.apiKey)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          const botMessage: ChatMessage = {
            id: Date.now() + 1,
            text: response.response,
            isUser: false,
            timestamp: response.timestamp,
            sources: response.sources
          };

          this.messages.push(botMessage);
          this.shouldScrollToBottom = true;
          this.loading = false;
        },
        error: (err) => {
          const errorMessage: ChatMessage = {
            id: Date.now() + 1,
            text: `Sorry, I encountered an error: ${err.message}`,
            isUser: false,
            timestamp: new Date().toISOString()
          };

          this.messages.push(errorMessage);
          this.shouldScrollToBottom = true;
          this.loading = false;
          this.error = err.message;
        }
      });
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  clearChat(): void {
    this.messages = [];
    this.error = null;
  }

  openSettings(): void {
    this.showSettings = true;
  }

  closeSettings(): void {
    this.showSettings = false;
  }

  saveApiKey(): void {
    if (this.apiKey) {
      localStorage.setItem('gemini_api_key', this.apiKey);
    }
  }

  setSampleQuestion(question: string): void {
    this.inputValue = question;
    if (this.messageInput) {
      this.messageInput.nativeElement.focus();
    }
  }

  private scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        const element = this.messagesContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }

  formatTime(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString();
  }
}
