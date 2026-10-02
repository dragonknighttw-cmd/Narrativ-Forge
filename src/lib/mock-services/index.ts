function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function mockLogin(email: string, password: string): Promise<{ success: boolean; error?: string }> {
  await delay(800);
  if (!email || !email.includes("@")) {
    return { success: false, error: "Please enter a valid email address." };
  }
  if (!password || password.length < 4) {
    return { success: false, error: "Password must be at least 4 characters." };
  }
  return { success: true };
}

export async function mockUpload(fileName: string): Promise<{ success: boolean; error?: string }> {
  await delay(1500);
  if (Math.random() > 0.85) {
    return { success: false, error: "Upload simulation failed. File format not supported." };
  }
  return { success: true };
}

export async function mockProcess(jobType: string): Promise<{ success: boolean; error?: string }> {
  await delay(2000);
  return { success: true };
}

export async function mockValidateSubtitles(): Promise<{ success: boolean; issues: number; critical: number }> {
  await delay(1200);
  return { success: true, issues: 4, critical: 2 };
}

export async function mockApprove(): Promise<{ success: boolean }> {
  await delay(600);
  return { success: true };
}

export async function mockExport(): Promise<{ success: boolean; folderId: string }> {
  await delay(2500);
  return { success: true, folderId: `mock_drive_folder_${Date.now().toString(36)}` };
}

export async function mockRender(): Promise<{ success: boolean }> {
  await delay(3000);
  return { success: true };
}
