import { NextResponse } from 'next/server';
import { verifyToken } from '@/src/lib/auth';
import { connectDB } from '@/src/lib/db';
import Job from '@/src/models/Job';

const ML_BACKEND_URL = process.env.ML_BACKEND_URL || 'http://127.0.0.1:8000';

export async function GET(request, { params }) {
  const auth = verifyToken(request);
  if (auth.error) {
    return NextResponse.json({ message: auth.error }, { status: 401 });
  }

  await connectDB();
  const { jobId } = await params;

  // Verify job belongs to user
  const job = await Job.findOne({
    jobId,
    labId: auth.user.userId
  });

  if (!job) {
    return NextResponse.json(
      { message: 'Report not found or access denied' },
      { status: 404 }
    );
  }

  if (job.status !== 'COMPLETED') {
    return NextResponse.json(
      { message: 'Report not ready yet' },
      { status: 400 }
    );
  }

  try {
    // Fetch PDF from ML backend
    const pdfResponse = await fetch(`${ML_BACKEND_URL}/api/reports/${jobId}/pdf`);
    
    if (!pdfResponse.ok) {
      throw new Error('Failed to fetch PDF from ML backend');
    }

    const pdfBuffer = await pdfResponse.arrayBuffer();

    return new NextResponse(pdfBuffer, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename=cytomind_report_${jobId}.pdf`
      }
    });

  } catch (error) {
    console.error('PDF Download Error:', error);
    return NextResponse.json(
      { message: 'Failed to download report' },
      { status: 500 }
    );
  }
}
