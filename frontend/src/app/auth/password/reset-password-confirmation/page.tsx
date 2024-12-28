"use client";


import ResetPasswordConfirmation from "@/app/components/ResetPasswordConfirmation";
import { Suspense } from "react";

export default function Home() {
  return (
    <main>
      <Suspense fallback={<div>Loading...</div>}>
      <ResetPasswordConfirmation />
      </Suspense>
    </main>
  );
}
