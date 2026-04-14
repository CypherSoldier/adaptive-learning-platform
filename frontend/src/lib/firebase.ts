// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBpY-mf8SuUntKwI6O4gW3kzEs7-OQPMnU",
  authDomain: "fitness-auth-312aa.firebaseapp.com",
  projectId: "fitness-auth-312aa",
  storageBucket: "fitness-auth-312aa.appspot.com",
  messagingSenderId: "458833306159",
  appId: "1:458833306159:web:89e139ffaea38726ed1cda"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();