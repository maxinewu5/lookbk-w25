// import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'
// import { getSignedUrl } from '@aws-sdk/s3-request-presigner'
// import { NextResponse } from 'next/server'
// import { prisma } from '@/db'

// const s3Client = new S3Client({
//   region: process.env.AWS_REGION!,
//   credentials: {
//     accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
//     secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
//   },
// })

// export async function POST(req: Request) {
//   try {
//     const { prompt, reactionType, demoType } = await req.json()

//     const fileName = `${Date.now()}-${Math.random().toString(36).substring(7)}.mp4`

//     // Create the S3 upload command
//     const command = new PutObjectCommand({
//       Bucket: process.env.AWS_BUCKET_NAME!,
//       Key: `uploads/${fileName}`,
//       ContentType: 'video/mp4',
//     })

//     // Generate presigned URL for frontend upload
//     const signedUrl = await getSignedUrl(s3Client, command, { expiresIn: 3600 })
    
//     // Create video record in database
//     const video = await prisma.video.create({
//       data: {
//         name: fileName,
//         url: `https://${process.env.AWS_BUCKET_NAME}.s3.${process.env.AWS_REGION}.amazonaws.com/uploads/${fileName}`,
//         prompt: prompt,
//         reaction: reactionType,
//         demoType: demoType,
//       },
//     })

//     return NextResponse.json({ 
//       signedUrl,
//       video
//     })

//   } catch (error) {
//     console.error('Error uploading video:', error)
//     return NextResponse.json(
//       { error: 'Failed to upload video' },
//       { status: 500 }
//     )
//   }
// }