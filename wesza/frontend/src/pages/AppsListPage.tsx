import { Link } from 'react-router-dom';

interface App {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  status: 'draft' | 'published' | 'building';
}

export default function AppsListPage() {
  // Sample apps - in production, fetch from API
  const apps: App[] = [];

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
              <Link to="/create-app" className="btn-primary">
                Create App
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Apps List */}
      <div className="container mx-auto px-6 py-12">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Apps</h1>
          <Link to="/create-app" className="btn-primary">
            + New App
          </Link>
        </div>

        {apps.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-6xl mb-4">📱</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No apps yet</h2>
            <p className="text-gray-600 mb-6">Create your first AI-powered mobile app today!</p>
            <Link to="/create-app" className="btn-primary inline-block">
              Create Your First App
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {apps.map((app) => (
              <div key={app.id} className="card">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{app.name}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    app.status === 'published' ? 'bg-green-100 text-green-800' :
                    app.status === 'building' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {app.status}
                  </span>
                </div>
                <p className="text-gray-600 mb-4 line-clamp-2">{app.description}</p>
                <p className="text-sm text-gray-500 mb-4">
                  Created: {new Date(app.createdAt).toLocaleDateString()}
                </p>
                <div className="flex gap-2">
                  <button className="btn-secondary flex-1 text-sm py-2">
                    Edit
                  </button>
                  <button className="btn-primary flex-1 text-sm py-2">
                    Publish
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
