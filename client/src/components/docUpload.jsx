import { useState } from 'react';
import { Upload, FileText } from 'lucide-react';



const DocumentUpload = ({ onUpload, title = "Upload Document" }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    
    setUploading(true);
    await onUpload(selectedFile);
    setUploading(false);
    setSelectedFile(null);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="text-center mb-6">
        <Upload className="mx-auto h-10 w-10 text-blue-600 mb-2" />
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>

      <form onSubmit={handleUpload} className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
          <input
            type="file"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <FileText className="mx-auto h-12 w-12 text-gray-400 mb-2" />
            <p className="text-gray-600">
              {selectedFile ? selectedFile.name : "Click to select a file"}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              PDF, DOC, DOCX, JPG, PNG up to 10MB
            </p>
          </label>
        </div>

        {selectedFile && (
          <button
            type="submit"
            disabled={uploading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition duration-200"
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        )}
      </form>
    </div>
  );
};

export default DocumentUpload;