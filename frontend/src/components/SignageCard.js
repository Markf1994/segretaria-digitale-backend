import React from 'react';

const SignageCard = ({ signage, onEdit, onDelete, type = 'temporary' }) => {
  const getQuantityColor = (quantity, minQuantity) => {
    if (quantity <= minQuantity) {
      return 'bg-red-100 text-red-800';
    } else if (quantity <= minQuantity * 2) {
      return 'bg-yellow-100 text-yellow-800';
    }
    return 'bg-green-100 text-green-800';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{signage.name}</h3>
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getQuantityColor(signage.quantity, signage.min_quantity)}`}>
            {signage.quantity} pz
          </span>
          {!signage.is_active && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              Inattivo
            </span>
          )}
        </div>
      </div>
      
      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <span className="font-medium mr-2">Tipo:</span>
          <span className="capitalize">{signage.type}</span>
        </div>
        
        {signage.code && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Codice:</span>
            <span>{signage.code}</span>
          </div>
        )}
        
        {signage.description && (
          <div className="flex items-start text-sm text-gray-600">
            <span className="font-medium mr-2">Descrizione:</span>
            <span className="flex-1">{signage.description}</span>
          </div>
        )}
        
        <div className="flex items-center text-sm text-gray-600">
          <span className="font-medium mr-2">Quantità minima:</span>
          <span>{signage.min_quantity}</span>
        </div>
        
        {signage.location && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Posizione:</span>
            <span>{signage.location}</span>
          </div>
        )}
        
        {signage.size && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Dimensioni:</span>
            <span>{signage.size}</span>
          </div>
        )}
        
        {signage.material && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Materiale:</span>
            <span>{signage.material}</span>
          </div>
        )}
        
        {signage.street_name && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Via:</span>
            <span>{signage.street_name}</span>
          </div>
        )}
        
        {signage.notes && (
          <div className="flex items-start text-sm text-gray-600">
            <span className="font-medium mr-2">Note:</span>
            <span className="flex-1">{signage.notes}</span>
          </div>
        )}
      </div>
      
      <div className="flex justify-end space-x-2">
        <button
          onClick={() => onEdit(signage)}
          className="px-3 py-1 bg-police-500 text-white rounded text-sm hover:bg-police-600 transition-colors"
        >
          Modifica
        </button>
        <button
          onClick={() => onDelete(signage.id)}
          className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600 transition-colors"
        >
          Elimina
        </button>
      </div>
    </div>
  );
};

export default SignageCard;