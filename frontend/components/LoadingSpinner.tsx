export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-gray-200 dark:border-gray-700 border-t-blue-500 rounded-full animate-spin"></div>
        <p className="mt-4 text-center text-gray-600 dark:text-gray-400">Loading...</p>
      </div>
    </div>
  )
}

