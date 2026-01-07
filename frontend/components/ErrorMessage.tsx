interface ErrorMessageProps {
  message: string
}

export default function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-lg p-6 max-w-md">
        <div className="flex items-center gap-3">
          <div className="text-red-500 text-2xl">⚠️</div>
          <div>
            <h3 className="text-lg font-semibold text-red-800 dark:text-red-200">Error</h3>
            <p className="text-sm text-red-600 dark:text-red-300 mt-1">{message}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

