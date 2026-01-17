import { NextResponse } from 'next/server';
import { connectDB } from '@/src/lib/db';
import { verifyToken } from '@/src/lib/auth';
import Job from '@/src/models/Job';
import Patient from '@/src/models/Patient';
import { randomUUID } from 'crypto';

const ML_BACKEND_URL = process.env.ML_BACKEND_URL || 'http://127.0.0.1:8000';

export async function POST(request) {
  const auth = verifyToken(request);
  if (auth.error) {
    return NextResponse.json({ message: auth.error }, { status: 401 });
  }

  await connectDB();
  
  const formData = await request.formData();
  
  // Get all images (supports both single 'image' and multiple 'images')
  const images = formData.getAll('images');
  const singleImage = formData.get('image');
  const allImages = images.length > 0 ? images : (singleImage ? [singleImage] : []);
  
  const patientId = formData.get('patientId');
  const name = formData.get('name');
  const age = formData.get('age');

  if (allImages.length === 0 || !patientId) {
    return NextResponse.json(
      { message: 'At least one image and patient ID are required' },
      { status: 400 }
    );
  }

  const jobId = randomUUID();

  // Create or update patient record
  await Patient.findOneAndUpdate(
    { patientId },
    { patientId, name, age, labId: auth.user.userId },
    { upsert: true, new: true }
  );

  // Create job record in database
  await Job.create({
    jobId,
    patientId,
    labId: auth.user.userId,
    status: 'PENDING',
    progress: 0,
    totalImages: allImages.length
  });

  // Forward to ML backend
  try {
    const mlFormData = new FormData();
    
    // Append all images
    allImages.forEach((image, index) => {
      mlFormData.append('images', image);
    });
    
    mlFormData.append('job_id', jobId);
    mlFormData.append('patient_id', patientId);
    mlFormData.append('patient_name', name || '');
    mlFormData.append('patient_age', age || '0');
    mlFormData.append('lab_id', auth.user.userId);

    const mlResponse = await fetch(`${ML_BACKEND_URL}/api/analyze`, {
      method: 'POST',
      body: mlFormData
    });

    if (!mlResponse.ok) {
      const errorData = await mlResponse.json();
      throw new Error(errorData.detail || 'ML backend error');
    }

    return NextResponse.json({
      jobId,
      status: 'PENDING',
      totalImages: allImages.length,
      message: `${allImages.length} image(s) uploaded, ML processing started`
    });

  } catch (error) {
    console.error('ML Backend Error:', error);
    
    // Update job status to failed
    await Job.findOneAndUpdate(
      { jobId },
      { status: 'FAILED', result: { error: error.message } }
    );

    return NextResponse.json(
      { message: 'Failed to start ML processing', error: error.message },
      { status: 500 }
    );
  }
}
