export const api = {
  // Generic API call wrapper
  async call(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers
    };

    try {
      const response = await fetch(endpoint, { ...options, headers });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'API request failed');
      }
      
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Upload single image with patient data
  async uploadImage(file, patientData) {
    return this.uploadImages([file], patientData);
  },

  // Upload multiple images with patient data
  async uploadImages(files, patientData) {
    const formData = new FormData();
    
    // Append all images
    files.forEach((file, index) => {
      formData.append('images', file);
    });
    
    formData.append('patientId', patientData.patientId);
    formData.append('name', patientData.name);
    formData.append('age', patientData.age);

    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Upload failed');
      }
      
      return data;
    } catch (error) {
      console.error('Upload Error:', error);
      throw error;
    }
  },

  // Get patient by ID
  async getPatient(patientId) {
    return this.call(`/api/patients/${patientId}`);
  },

  // Get job status
  async getJobStatus(jobId) {
    return this.call(`/api/jobs/${jobId}/status`);
  },

  // Download report
  async downloadReport(jobId) {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`/api/reports/${jobId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cytomind_report_${jobId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download Error:', error);
      throw error;
    }
  }
};