import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import Chat from '../components/Chat';

const InstallationGuide = () => {
  const { part_number } = useParams();
  const [guide, setGuide] = useState(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    const fetchGuide = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/products/${part_number}/installation-guide/`);
        const data = await response.json();
        setGuide(data);
      } catch (error) {
        console.error('Error fetching guide:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGuide();
  }, [part_number]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Guide Content */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h1 className="text-2xl font-bold mb-4">
            Installation Guide for {guide.product.name}
          </h1>
          <div className="prose max-w-none">
            {guide.content.split('\n').map((paragraph, idx) => (
              <p key={idx} className="mb-4">{paragraph}</p>
            ))}
          </div>
        </div>

        {/* Chat Integration */}
        <div className="h-full bg-white rounded-lg shadow">
          <Chat currentUrl={location.pathname} />
        </div>
      </div>
    </div>
  );
};

export default InstallationGuide;