import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-indigo-800">
      {/* Navigation */}
      <nav className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="text-white text-2xl font-bold">Wesza</div>
          <div className="space-x-4">
            <Link to="/dashboard" className="text-white hover:text-blue-200 transition-colors">
              Dashboard
            </Link>
            <Link to="/my-apps" className="text-white hover:text-blue-200 transition-colors">
              My Apps
            </Link>
            <Link to="/create-app" className="btn-primary bg-white text-blue-600 hover:bg-blue-50">
              Create App
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Build Mobile Apps with AI
        </h1>
        <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
          Wesza is the AI-powered no-code platform that lets you create beautiful mobile apps in minutes. No coding required.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/create-app" className="btn-primary bg-white text-blue-600 hover:bg-blue-50 text-lg px-8 py-4">
            Start Building Free
          </Link>
          <Link to="/dashboard" className="btn-secondary bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-600 text-lg px-8 py-4">
            View Demo
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-6 py-20">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">AI-Powered</h3>
            <p className="text-gray-600">Describe your app in natural language and let our AI build it for you.</p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
            <p className="text-gray-600">Go from idea to deployed app in minutes, not months.</p>
          </div>
          <div className="card text-center">
            <div className="text-4xl mb-4">📱</div>
            <h3 className="text-xl font-semibold mb-2">Mobile Ready</h3>
            <p className="text-gray-600">Create responsive apps that work perfectly on all devices.</p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-6 py-20 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Ready to Build Your First App?</h2>
        <p className="text-blue-100 mb-8">Join thousands of creators building apps with Wesza.</p>
        <Link to="/create-app" className="btn-primary bg-white text-blue-600 hover:bg-blue-50 text-lg px-8 py-4">
          Get Started Now
        </Link>
      </div>
    </div>
  );
}
