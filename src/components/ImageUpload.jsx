import React, { useState } from 'react';
import { FileUp, AlertCircle, X, Image } from 'lucide-react';
import { api } from '../lib/api';

const ImageUpload = ({ patientData, onUploadComplete }) => {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    if (selectedFiles.length === 0) return;

    // Validate each file
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff'];
    const maxSize = 50 * 1024 * 1024; // 50MB per file
    
    const validFiles = [];
    const newPreviews = [];
    
    for (const file of selectedFiles) {
      if (!validTypes.includes(file.type)) {
        setError(`${file.name}: Invalid file type. Only JPG, PNG, or TIFF allowed.`);
        continue;
      }
      if (file.size > maxSize) {
        setError(`${file.name}: File size must be less than 50MB`);
        continue;
      }
      validFiles.push(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        newPreviews.push({ name: file.name, url: reader.result });
        if (newPreviews.length === validFiles.length) {
          setPreviews(prev => [...prev, ...newPreviews]);
        }
      };
      reader.readAsDataURL(file);
    }
    
    if (validFiles.length > 0) {
      setError('');
      setFiles(prev => [...prev, ...validFiles]);
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0 || !patientData) {
      setError('Please select at least one image and enter patient data');
      return;
    }
    
    setUploading(true);
    setError('');

    try {
      const result = await api.uploadImages(files, patientData);
      onUploadComplete(result);
    } catch (error) {
      setError(error.message || 'Upload failed. Please try again.');
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Bone Marrow Images</h2>
      <p className="text-sm text-gray-600 mb-4">Select multiple cell images for comprehensive analysis</p>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition">
        <input
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/tiff"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload"
          disabled={uploading}
          multiple
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <FileUp className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 mb-2 font-medium">
            Click to upload or drag and drop
          </p>
          <p className="text-sm text-gray-500">JPG, PNG or TIFF (max 50MB each)</p>
          <p className="text-xs text-indigo-600 mt-2">You can select multiple images</p>
        </label>
      </div>

      {/* Selected files count */}
      {files.length > 0 && (
        <div className="mt-4 flex items-center justify-between bg-indigo-50 px-4 py-2 rounded-lg">
          <span className="text-indigo-700 font-medium">
            <Image className="w-4 h-4 inline mr-2" />
            {files.length} image{files.length > 1 ? 's' : ''} selected
          </span>
          <button
            onClick={() => { setFiles([]); setPreviews([]); }}
            className="text-sm text-red-600 hover:text-red-800"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Previews grid */}
      {previews.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Selected Images:</p>
          <div className="grid grid-cols-3 gap-3 max-h-64 overflow-y-auto">
            {previews.map((preview, index) => (
              <div key={index} className="relative group">
                <img 
                  src={preview.url} 
                  alt={preview.name} 
                  className="w-full h-24 object-cover rounded-lg border border-gray-200" 
                />
                <button
                  onClick={() => removeFile(index)}
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition"
                >
                  <X className="w-3 h-3" />
                </button>
                <p className="text-xs text-gray-500 truncate mt-1">{preview.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={files.length === 0 || uploading || !patientData}
        className="w-full mt-4 bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {uploading ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
            Uploading and Processing {files.length} image{files.length > 1 ? 's' : ''}...
          </>
        ) : (
          `Upload and Analyze ${files.length > 0 ? `(${files.length} image${files.length > 1 ? 's' : ''})` : ''}`
        )}
      </button>
    </div>
  );
};

export default ImageUpload;