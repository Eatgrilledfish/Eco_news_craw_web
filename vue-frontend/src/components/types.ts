// types.ts
import type { Ref } from 'vue';

export interface NewsItem {
    id: number;
    title: string;
    publish_time: string; 
    content: string;
    url: string;        // 新闻的链接
    key_word: string;
    source: string;
    // 可以根据需要添加更多字段
  }
  
  export interface ComponentData {
    activeIndex: Ref<string>;
    newsCount: number;
    wordsCount: number;
  }
  
  export interface ApiResponse {
    data: NewsItem[];
    message: string; // API 响应中可能包含的消息
    // 根据你的 API 设计，可以添加更多字段
  }
  