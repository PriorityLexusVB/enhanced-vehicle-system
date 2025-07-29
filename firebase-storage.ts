// firebase-storage.ts
import { getStorage, ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { app } from "./firebaseconfig"; // make sure this path matches your structure

const storage = getStorage(app);

export const uploadPhoto = async (file: File, userId: string, label: string) => {
  const storageRef = ref(storage, `trade-ins/${userId}/${label}-${Date.now()}`);
  await uploadBytes(storageRef, file);
  return await getDownloadURL(storageRef);
};
