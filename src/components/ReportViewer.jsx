import React, { useState } from 'react';
import { Download, AlertCircle, TrendingUp } from 'lucide-react';
import { api } from '../lib/api';

const ReportViewer = ({ report }) => {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');

  const handleDownload = async () => {
    setDownloading(true);
    setError('');

    try {
      await api.downloadReport(report.jobId);
    } catch (error) {
      setError('Download failed. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  if (!report) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6 text-center text-gray-500">
        No report available
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Diagnostic Report</h2>
      
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div>
          <p className="text-sm text-gray-600 mb-1">Patient ID</p>
          <p className="text-lg font-semibold text-gray-900">{report.patientId}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">Patient Name</p>
          <p className="text-lg font-semibold text-gray-900">{report.patientName}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">Age</p>
          <p className="text-lg font-semibold text-gray-900">{report.age} years</p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">Analysis Date</p>
          <p className="text-lg font-semibold text-gray-900">
            {new Date(report.date).toLocaleDateString()}
          </p>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-6">
        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-3">Classification Result</p>
          <div className={`inline-block px-6 py-3 rounded-full text-lg font-bold ${
            report.classification === 'MALIGNANT' 
              ? 'bg-red-100 text-red-800 border-2 border-red-300' 
              : 'bg-green-100 text-green-800 border-2 border-green-300'
          }`}>
            {report.classification}
          </div>
        </div>

        {/* Primary Cell Type */}
        <div className="mb-6 bg-indigo-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-2">Primary Cell Type Detected</p>
          <p className="text-xl font-bold text-indigo-700">
            {report.primaryClassFullName || report.primaryClass}
          </p>
          <p className="text-sm text-indigo-600">({report.primaryClass})</p>
        </div>

        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-3">Malignancy Percentage</p>
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-10 overflow-hidden">
              <div
                className="bg-gradient-to-r from-yellow-400 via-orange-500 to-red-600 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm transition-all duration-500"
                style={{ width: `${Math.min(report.malignancyPercentage, 100)}%` }}
              >
                {report.malignancyPercentage >= 15 && `${report.malignancyPercentage}%`}
              </div>
            </div>
            {report.malignancyPercentage < 15 && (
              <span className="ml-3 font-bold text-gray-700">
                {report.malignancyPercentage}%
              </span>
            )}
          </div>
        </div>

        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-2">Confidence Score</p>
          <p className="text-3xl font-bold text-indigo-600">{report.confidence}%</p>
        </div>

        {/* Top Predictions */}
        {report.topPredictions && report.topPredictions.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center mb-3">
              <TrendingUp className="w-5 h-5 text-gray-600 mr-2" />
              <p className="text-sm font-medium text-gray-600">Top Predictions</p>
            </div>
            <div className="space-y-2">
              {report.topPredictions.slice(0, 5).map((pred, index) => (
                <div key={index} className="flex items-center">
                  <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-sm mr-3">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700">
                        {pred.class_full_name || pred.class}
                      </span>
                      <span className="text-sm font-bold text-indigo-600">
                        {pred.probability?.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-indigo-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${pred.probability}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      <button
        onClick={handleDownload}
        disabled={downloading}
        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {downloading ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
            Downloading...
          </>
        ) : (
          <>
            <Download className="w-5 h-5 mr-2" />
            Download Full Report (PDF)
          </>
        )}
      </button>
    </div>
  );
};

export default ReportViewer;