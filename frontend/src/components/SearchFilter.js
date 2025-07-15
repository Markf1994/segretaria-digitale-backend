import React from 'react';

const SearchFilter = ({ 
  searchTerm, 
  onSearchChange, 
  typeFilter, 
  onTypeChange, 
  locationFilter, 
  onLocationChange,
  statusFilter, 
  onStatusChange,
  typeOptions = [],
  statusOptions = [],
  placeholder = "Cerca...",
  showStatus = true,
  showType = true,
  showLocation = true 
}) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-md mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search Input */}
        <div className="col-span-1 md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ricerca
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={placeholder}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-police-500 focus:border-transparent"
          />
        </div>

        {/* Type Filter */}
        {showType && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo
            </label>
            <select
              value={typeFilter}
              onChange={(e) => onTypeChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-police-500 focus:border-transparent"
            >
              <option value="">Tutti i tipi</option>
              {typeOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Status Filter */}
        {showStatus && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stato
            </label>
            <select
              value={statusFilter}
              onChange={(e) => onStatusChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-police-500 focus:border-transparent"
            >
              <option value="">Tutti gli stati</option>
              {statusOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Location Filter */}
        {showLocation && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Posizione
            </label>
            <input
              type="text"
              value={locationFilter}
              onChange={(e) => onLocationChange(e.target.value)}
              placeholder="Filtra per posizione"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-police-500 focus:border-transparent"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchFilter;