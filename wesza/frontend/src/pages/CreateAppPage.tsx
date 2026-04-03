import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function CreateAppPage() {
  const navigate = useNavigate();
  const [appName, setAppName] = useState('');
  const [description, setDescription] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    
    // Simulate AI app generation
    setTimeout(() => {
      setIsGenerating(false);
      navigate('/my-apps');
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="text-2xl font-bold text-blue-600">Wesza</Link>
            <div className="space-x-4">
              <Link to="/dashboard" className="text-gray-600 hover:text-blue-600 transition-colors">
                Dashboard
              </Link>
              <Link to="/my-apps" className="text-gray-600 hover:text-blue-600 transition-colors">
                My Apps
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Create App Form */}
      <div className="container mx-auto px-6 py-12">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Create New App</h1>
          
          <div className="card">
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label htmlFor="appName" className="block text-sm font-medium text-gray-700 mb-2">
                  App Name
                </label>
                <input
                  type="text"
                  id="appName"
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  className="input-field"
                  placeholder="My Awesome App"
                  required
                />
              </div>

              <div className="mb-6">
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Describe Your App
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="input-field h-32 resize-none"
                  placeholder="Describe what your app should do. Our AI will build it for you..."
                  required
                />
                <p className="text-sm text-gray-500 mt-2">
                  Be as detailed as possible. Include features, target audience, and desired functionality.
                </p>
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={isGenerating || !appName || !description}
                  className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isGenerating ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating with AI...
                    </span>
                  ) : (
                    'Generate App'
                  )}
                </button>
                <Link to="/dashboard" className="btn-secondary">
                  Cancel
                </Link>
              </div>
            </form>
          </div>

          <div className="mt-8 card bg-blue-50 border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">How it works</h3>
            <ol className="list-decimal list-inside space-y-2 text-blue-800">
              <li>Enter your app name and description</li>
              <li>Our AI analyzes your requirements</li>
              <li>Automatic code generation and UI design</li>
              <li>Instant deployment to wesza.online</li>
              <li>Download as mobile app or share via link</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
