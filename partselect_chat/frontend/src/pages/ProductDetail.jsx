import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import Chat from '../components/Chat';

const ProductDetail = () => {
  const { part_number } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/products/${part_number}/`);
        console.log('response', response);
        const data = await response.json();
        setProduct(data);
      } catch (error) {
        console.error('Error fetching product:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [part_number]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Product Details */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h1 className="text-2xl font-bold mb-4">{product.name}</h1>
          <div className="mb-4">
            <img 
              src={`/api/placeholder/400/300`}
              alt={product.name}
              className="w-full rounded-lg" 
            />
          </div>
          <div className="space-y-2">
            <p className="text-lg">Part Number: {product.part_number}</p>
            <p className="text-xl font-semibold">${product.price}</p>
            <p className="text-gray-600">{product.description}</p>
            <p className="text-sm">
              Stock: {product.stock_quantity > 0 ? 'In Stock' : 'Out of Stock'}
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ProductDetail;