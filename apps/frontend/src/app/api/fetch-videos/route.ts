import { NextResponse } from 'next/server'
import { prisma } from "@/db"

export async function GET(req: Request) {
  try {
    // Get query parameters
    const { searchParams } = new URL(req.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '10')
    const reaction = searchParams.get('reaction')
    const demoType = searchParams.get('demoType')

    // Build where clause based on filters
    const where = {
      ...(reaction && { reaction }),
      ...(demoType && { demoType }),
    }

    // Get total count for pagination
    const total = await prisma.video.count({ where })

    // Get videos with pagination
    const videos = await prisma.video.findMany({
      where,
      orderBy: {
        id: 'desc',
      },
      skip: (page - 1) * limit,
      take: limit,
    })

    return NextResponse.json({
      videos,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    })

  } catch (error) {
    console.error('Error fetching videos:', error)
    return NextResponse.json(
      { error: 'Failed to fetch videos' },
      { status: 500 }
    )
  }
}