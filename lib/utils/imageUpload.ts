import { ref, uploadBytes, getDownloadURL } from "firebase/storage"
import { storage } from "@/lib/firebaseconfig";

export const uploadImage = async (file: File, folder: string): Promise<string> => {
  const fileName = `${Date.now()}_${file.name}`
  const fileRef = ref(storage, `${folder}/${fileName}`)

  await uploadBytes(fileRef, file)
  return await getDownloadURL(fileRef)
}

export const uploadMultipleImages = async (files: { [key: string]: File | null }, folder: string) => {
  const uploadPromises: Promise<{ field: string; url: string }>[] = []

  Object.entries(files).forEach(([field, file]) => {
    if (file) {
      uploadPromises.push(uploadImage(file, folder).then((url) => ({ field, url })))
    }
  })

  const results = await Promise.all(uploadPromises)
  const photoUrls: { [key: string]: string } = {}
  results.forEach(({ field, url }) => (photoUrls[field] = url))
  return photoUrls
}
