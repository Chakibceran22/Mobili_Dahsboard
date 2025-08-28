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
import { AiVisualizerService, VisualizationMessage } from './ai-visualizer.service';
import { Subject, interval } from 'rxjs';
import { takeUntil, switchMap } from 'rxjs/operators';

@Component({
  selector: 'tb-ai-assistant',
  templateUrl: './ai-assistant.component.html',
  styleUrls: ['./ai-assistant.component.scss']
})
export class AiAssistantComponent implements OnInit, AfterViewChecked, OnDestroy {
  @ViewChild('messagesContainer') private messagesContainer: ElementRef;
  @ViewChild('messageInput') private messageInput: ElementRef;
  @ViewChild('visualizeMessagesContainer') private visualizeMessagesContainer: ElementRef;
  @ViewChild('visualizeMessageInput') private visualizeMessageInput: ElementRef;

  // Chat page properties
  messages: ChatMessage[] = [];
  inputValue = '';
  apiKey = '';
  showSettings = false;
  loading = false;
  error: string | null = null;
  dbStatus: DatabaseStatus | null = null;

  // Visualize page properties
  visualizeMessages: VisualizationMessage[] = [];
  visualizeInputValue = '';
  visualizeLoading = false;
  visualizeError: string | null = null;

  // Page toggle functionality
  currentPage: 'chat' | 'visualize' = 'chat';

  private destroy$ = new Subject<void>();
  private shouldScrollToBottom = false;
  private shouldScrollVisualizerToBottom = false;

  sampleQuestions = [
    "How do I connect a device to Mobilis?",
    "What is device provisioning?",
    "How to use MQTT with Mobilis?",
    "How to create a dashboard?"
  ];

  visualizeSampleQuestions = [
    "Show me battery data for the last 7 days",
    "Plot temperature data for today",
    "Create a bar chart of humidity levels",
    "Display battery levels for the last 3 hours"
  ];

  constructor(
    private aiChatService: AiChatService,
    private aiVisualizerService: AiVisualizerService
  ) {
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
    if (this.shouldScrollVisualizerToBottom) {
      this.scrollVisualizerToBottom();
      this.shouldScrollVisualizerToBottom = false;
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

  // Visualizer methods
  sendVisualizationMessage(): void {
    if (!this.visualizeInputValue.trim() || this.visualizeLoading) {
      return;
    }

    const userMessage: VisualizationMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: this.visualizeInputValue,
      timestamp: new Date().toISOString()
    };

    this.visualizeMessages.push(userMessage);
    const prompt = this.visualizeInputValue;
    this.visualizeInputValue = '';
    this.visualizeLoading = true;
    this.visualizeError = null;
    this.shouldScrollVisualizerToBottom = true;

    this.aiVisualizerService.sendVisualizationRequest(prompt).subscribe({
      next: (response) => {
        const botMessage: VisualizationMessage = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          content: response.message || 'Visualization generated successfully',
          timestamp: new Date().toISOString(),
          plotUrl: response.plot_url,
          details: response.details
        };

        this.visualizeMessages.push(botMessage);
        this.visualizeLoading = false;
        this.shouldScrollVisualizerToBottom = true;
      },
      error: (error) => {
        const errorMessage: VisualizationMessage = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          content: `Error: ${error}`,
          timestamp: new Date().toISOString()
        };

        this.visualizeMessages.push(errorMessage);
        this.visualizeLoading = false;
        this.visualizeError = error;
        this.shouldScrollVisualizerToBottom = true;
      }
    });
  }

  onVisualizerKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendVisualizationMessage();
    }
  }

  clearVisualizerMessages(): void {
    this.visualizeMessages = [];
    this.visualizeError = null;
  }

  setVisualizeSampleQuestion(question: string): void {
    this.visualizeInputValue = question;
    if (this.visualizeMessageInput) {
      this.visualizeMessageInput.nativeElement.focus();
    }
  }

  private scrollVisualizerToBottom(): void {
    try {
      if (this.visualizeMessagesContainer) {
        const element = this.visualizeMessagesContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      console.error('Error scrolling visualizer to bottom:', err);
    }
  }

  // Page toggle methods
  switchToChat(): void {
    this.currentPage = 'chat';
  }

  switchToVisualize(): void {
    this.currentPage = 'visualize';
  }

  formatTime(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString();
  }
}
