import { NextResponse } from 'next/server';
import { connectDB } from '@/src/lib/db';
import { verifyToken } from '@/src/lib/auth';
import Job from '@/src/models/Job';
import Patient from '@/src/models/Patient';

export async function GET(request, { params }) {
  const auth = verifyToken(request);
  if (auth.error) {
    return NextResponse.json({ message: auth.error }, { status: 401 });
  }

  await connectDB();
  const { jobId } = await params;

  const job = await Job.findOne({
    jobId,
    labId: auth.user.userId
  });

  if (!job) {
    return NextResponse.json(
      { message: 'Job not found or access denied' },
      { status: 404 }
    );
  }

  // Build response
  const response = {
    jobId: job.jobId,
    status: job.status,
    progress: job.progress || 0
  };

  // If completed, include report data
  if (job.status === 'COMPLETED' && job.result) {
    // Get patient info
    const patient = await Patient.findOne({ patientId: job.patientId });
    
    response.report = {
      jobId: job.jobId,
      patientId: job.patientId,
      patientName: patient?.name || 'N/A',
      age: patient?.age || 'N/A',
      date: job.createdAt,
      classification: job.result.classification,
      primaryClass: job.result.primaryClass,
      primaryClassFullName: job.result.primaryClassFullName,
      malignancyPercentage: job.result.malignancyPercentage,
      confidence: job.result.confidence,
      topPredictions: job.result.topPredictions
    };
  }

  // If failed, include error message
  if (job.status === 'FAILED' && job.result?.error) {
    response.message = job.result.error;
  }

  return NextResponse.json(response);
}
