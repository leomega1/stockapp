'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorMessage from '@/components/ErrorMessage'
import { format } from 'date-fns'
import { useParams } from 'next/navigation'
import Link from 'next/link'

export default function ArticlePage() {
  const params = useParams()
  const slug = params.slug as string

  // Fetch article by SEO-friendly slug
  const { data: article, isLoading: articlesLoading, error: articlesError } = useQuery({
    queryKey: ['article', slug],
    queryFn: () => api.getArticleBySlug(slug),
  })

  // Get symbol from article once loaded
  const symbol = article?.stock_symbol

  // Fetch stock data
  const { data: stock, isLoading: stockLoading } = useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => symbol ? api.getStockBySymbol(symbol) : Promise.resolve(null),
    enabled: !!symbol,
  })

  // Fetch news for the stock
  const { data: news, isLoading: newsLoading } = useQuery({
    queryKey: ['news', symbol],
    queryFn: () => symbol ? api.getStockNews(symbol) : Promise.resolve([]),
    retry: false,
    enabled: !!symbol,
  })

  if (articlesLoading || stockLoading) {
    return <LoadingSpinner />
  }

  if (articlesError || !article) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <ErrorMessage 
          message={`Article not found. The URL may be invalid or the article has not been generated yet.`} 
        />
        <div className="text-center mt-6">
          <Link 
            href="/"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }
  const isWinner = article.movement_type === 'winner'
  const bgColor = isWinner ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'
  const borderColor = isWinner ? 'border-green-200 dark:border-green-800' : 'border-red-200 dark:border-red-800'
  const textColor = isWinner ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
  const badgeColor = isWinner ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'

  const changePercent = stock ? stock.price_change_pct.toFixed(2) : article.stock_change_pct?.toFixed(2) || '0.00'
  const price = stock ? stock.price.toFixed(2) : article.stock_price?.toFixed(2) || '0.00'
  const stockName = stock?.name || article.stock_name || symbol
  const articleDate = format(new Date(article.date), 'MMMM dd, yyyy')

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Back Button */}
      <Link 
        href="/"
        className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:underline mb-6"
      >
        ← Back to Dashboard
      </Link>

      {/* Stock Header */}
      <div className={`${bgColor} ${borderColor} border-2 rounded-lg p-8 mb-8`}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className={`${badgeColor} text-sm font-bold px-3 py-1 rounded-full`}>
                {isWinner ? '🚀 WINNER' : '📉 LOSER'}
              </span>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {symbol}
              </h1>
            </div>
            <p className="text-xl text-gray-700 dark:text-gray-200">{stockName}</p>
          </div>
          <div className="text-right">
            <p className={`text-4xl font-bold ${textColor}`}>
              {changePercent > '0' ? '+' : ''}{changePercent}%
            </p>
            <p className="text-lg text-gray-600 dark:text-gray-300 mt-2">
              ${price}
            </p>
          </div>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-4">
          {articleDate}
        </p>
      </div>

      {/* Article Content */}
      <article className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          {article.title}
        </h2>
        
        <div className="prose prose-lg dark:prose-invert max-w-none">
          {article.content.split('\n\n').map((paragraph, index) => (
            <p key={index} className="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">
              {paragraph}
            </p>
          ))}
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Article generated on {format(new Date(article.created_at), 'MMMM dd, yyyy \'at\' h:mm a')}
          </p>
        </div>
      </article>

      {/* Related News */}
      {!newsLoading && news && news.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
            📰 Related News
          </h3>
          
          <div className="space-y-4">
            {news.slice(0, 5).map((item) => (
              <div 
                key={item.id}
                className="border-l-4 border-blue-500 pl-4 py-2"
              >
                <a 
                  href={item.url || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  {item.headline}
                </a>
                {item.source && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Source: {item.source}
                  </p>
                )}
                {item.summary && (
                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
                    {item.summary}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Note */}
      <div className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className="text-2xl">⚠️</div>
          <div>
            <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
              Disclaimer
            </h3>
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              This article was generated by AI based on stock price movements and recent news. 
              It should not be considered investment advice. Always conduct your own research 
              and consult with a financial advisor before making investment decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

