'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import StockCard from '@/components/StockCard'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorMessage from '@/components/ErrorMessage'
import { format } from 'date-fns'

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dailyMovers'],
    queryFn: () => api.getDailyMovers(),
  })

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <ErrorMessage 
        message="Failed to load stock data. The backend API may be starting up or there may be no data yet. Please try again in a moment." 
      />
    )
  }

  const currentDate = data?.date ? format(new Date(data.date), 'MMMM dd, yyyy') : format(new Date(), 'MMMM dd, yyyy')

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          S&P 500 Daily Movers
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          {currentDate}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          AI-generated insights on today's biggest stock movements
        </p>
      </div>

      {/* Winners Section */}
      <section className="mb-12">
        <div className="flex items-center gap-3 mb-6">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            🚀 Biggest Winners
          </h2>
          <span className="bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100 text-sm font-semibold px-3 py-1 rounded-full">
            Top {data?.winners?.length || 0}
          </span>
        </div>
        
        {data?.winners && data.winners.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.winners.map((stock, index) => (
              <StockCard 
                key={stock.id} 
                stock={stock} 
                type="winner"
                rank={index + 1}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-500 dark:text-gray-400 text-center py-8">
            No winners data available yet.
          </p>
        )}
      </section>

      {/* Losers Section */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            📉 Biggest Losers
          </h2>
          <span className="bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100 text-sm font-semibold px-3 py-1 rounded-full">
            Top {data?.losers?.length || 0}
          </span>
        </div>
        
        {data?.losers && data.losers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.losers.map((stock, index) => (
              <StockCard 
                key={stock.id} 
                stock={stock} 
                type="loser"
                rank={index + 1}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-500 dark:text-gray-400 text-center py-8">
            No losers data available yet.
          </p>
        )}
      </section>

      {/* Info Box */}
      <div className="mt-12 bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className="text-3xl">💡</div>
          <div>
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
              How It Works
            </h3>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              We analyze all S&P 500 stocks daily to identify the biggest movers. 
              Click on any stock card to read an AI-generated article explaining 
              why the stock moved and the key factors driving the change.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

