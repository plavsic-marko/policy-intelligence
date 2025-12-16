interface ErrorBannerProps {
  message: string | null;
}

const ErrorBanner = ({ message }: ErrorBannerProps) => {
  if (!message) return null;

  return (
    <div className="bg-red-900/40 text-red-300 px-4 py-3 rounded-lg mb-6">
      {message}
    </div>
  );
};

export default ErrorBanner;
