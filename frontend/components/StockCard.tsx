'use client'

import { Stock } from '@/lib/api'
import Link from 'next/link'

interface StockCardProps {
  stock: Stock
  type: 'winner' | 'loser'
  rank: number
}

export default function StockCard({ stock, type, rank }: StockCardProps) {
  const isWinner = type === 'winner'
  const bgColor = isWinner ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'
  const borderColor = isWinner ? 'border-green-200 dark:border-green-800' : 'border-red-200 dark:border-red-800'
  const textColor = isWinner ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
  const badgeColor = isWinner ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'

  const formattedChange = stock.price_change_pct > 0 ? `+${stock.price_change_pct.toFixed(2)}%` : `${stock.price_change_pct.toFixed(2)}%`
  const formattedPrice = `$${stock.price.toFixed(2)}`
  const formattedVolume = new Intl.NumberFormat('en-US', { notation: 'compact' }).format(stock.volume)

  return (
    <Link href={`/article/${stock.symbol}`}>
      <div className={`${bgColor} ${borderColor} border-2 rounded-lg p-6 hover:shadow-lg transition-all duration-200 cursor-pointer transform hover:-translate-y-1`}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className={`${badgeColor} text-xs font-bold px-2 py-1 rounded`}>
                #{rank}
              </span>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">{stock.symbol}</h3>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-300">{stock.name}</p>
          </div>
          <div className="text-right">
            <p className={`text-2xl font-bold ${textColor}`}>
              {formattedChange}
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Price</p>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">{formattedPrice}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Volume</p>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">{formattedVolume}</p>
          </div>
        </div>

        <div className="mt-4">
          <span className={`text-sm font-medium ${textColor} flex items-center justify-center`}>
            Read Article →
          </span>
        </div>
      </div>
    </Link>
  )
}

