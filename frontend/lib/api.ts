const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Stock {
  id: number
  symbol: string
  name: string
  date: string
  price: number
  price_change: number
  price_change_pct: number
  volume: number
}

export interface Article {
  id: number
  stock_symbol: string
  date: string
  title: string
  content: string
  movement_type: 'winner' | 'loser'
  slug: string | null
  created_at: string
  stock_name?: string
  stock_price?: number
  stock_change_pct?: number
}

export interface DailyMovers {
  date: string
  winners: Stock[]
  losers: Stock[]
}

export interface NewsItem {
  id: number
  headline: string
  url: string | null
  source: string | null
  summary: string | null
  created_at: string
}

class APIClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  private async fetch<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`)
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }
    return response.json()
  }

  async getDailyMovers(date?: string): Promise<DailyMovers> {
    const query = date ? `?date=${date}` : ''
    return this.fetch<DailyMovers>(`/api/stocks/daily${query}`)
  }

  async getStockBySymbol(symbol: string, date?: string): Promise<Stock> {
    const query = date ? `?date=${date}` : ''
    return this.fetch<Stock>(`/api/stocks/${symbol}${query}`)
  }

  async getDailyArticles(date?: string): Promise<Article[]> {
    const query = date ? `?date=${date}` : ''
    return this.fetch<Article[]>(`/api/articles/daily${query}`)
  }

  async getArticleById(id: number): Promise<Article> {
    return this.fetch<Article>(`/api/articles/${id}`)
  }

  async getArticlesBySymbol(symbol: string, limit: number = 10): Promise<Article[]> {
    return this.fetch<Article[]>(`/api/articles/stock/${symbol}?limit=${limit}`)
  }

  async getArticleBySlug(slug: string): Promise<Article> {
    return this.fetch<Article>(`/api/articles/slug/${slug}`)
  }

  async getStockNews(symbol: string): Promise<NewsItem[]> {
    return this.fetch<NewsItem[]>(`/api/articles/stock/${symbol}/news`)
  }

  async fetchMovers(topN: number = 5): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/stocks/fetch-movers?top_n=${topN}`, {
      method: 'POST'
    })
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }
    return response.json()
  }
}

export const api = new APIClient(API_URL)

