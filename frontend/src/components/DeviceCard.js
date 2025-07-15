import React from 'react';

const DeviceCard = ({ device, onEdit, onDelete }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'disponibile':
        return 'bg-green-100 text-green-800';
      case 'in uso':
        return 'bg-yellow-100 text-yellow-800';
      case 'in manutenzione':
        return 'bg-orange-100 text-orange-800';
      case 'fuori servizio':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{device.name}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(device.status)}`}>
          {device.status}
        </span>
      </div>
      
      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <span className="font-medium mr-2">Tipo:</span>
          <span className="capitalize">{device.type}</span>
        </div>
        
        {device.brand && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Marca:</span>
            <span>{device.brand}</span>
          </div>
        )}
        
        {device.model && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Modello:</span>
            <span>{device.model}</span>
          </div>
        )}
        
        {device.serial_number && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Numero seriale:</span>
            <span>{device.serial_number}</span>
          </div>
        )}
        
        {device.location && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Posizione:</span>
            <span>{device.location}</span>
          </div>
        )}
        
        {device.notes && (
          <div className="flex items-start text-sm text-gray-600">
            <span className="font-medium mr-2">Note:</span>
            <span className="flex-1">{device.notes}</span>
          </div>
        )}
      </div>
      
      <div className="flex justify-end space-x-2">
        <button
          onClick={() => onEdit(device)}
          className="px-3 py-1 bg-police-500 text-white rounded text-sm hover:bg-police-600 transition-colors"
        >
          Modifica
        </button>
        <button
          onClick={() => onDelete(device.id)}
          className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600 transition-colors"
        >
          Elimina
        </button>
      </div>
    </div>
  );
};

export default DeviceCard;