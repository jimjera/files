import { Link } from 'react-router-dom';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="text-2xl font-bold text-blue-600">Wesza</Link>
            <div className="space-x-4">
              <Link to="/my-apps" className="text-gray-600 hover:text-blue-600 transition-colors">
                My Apps
              </Link>
              <Link to="/create-app" className="btn-primary">
                Create App
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Dashboard Content */}
      <div className="container mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
        
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Total Apps</h3>
            <p className="text-4xl font-bold text-blue-600">0</p>
            <p className="text-gray-500 mt-2">Start creating your first app</p>
          </div>
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">API Calls</h3>
            <p className="text-4xl font-bold text-green-600">0</p>
            <p className="text-gray-500 mt-2">This month</p>
          </div>
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Storage Used</h3>
            <p className="text-4xl font-bold text-purple-600">0 MB</p>
            <p className="text-gray-500 mt-2">of 1 GB free tier</p>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Quick Start</h2>
          <p className="text-gray-600 mb-6">Create your first AI-powered mobile app in minutes.</p>
          <Link to="/create-app" className="btn-primary inline-block">
            Create Your First App
          </Link>
        </div>
      </div>
    </div>
  );
}
