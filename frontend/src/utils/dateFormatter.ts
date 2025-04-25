export const formatDateTime = (dateTimeString: string | null | undefined): string => {
  if (!dateTimeString) return 'Unknown date';
  try {
    // Format to locale date string (e.g., '12/31/2023')
    return new Date(dateTimeString).toLocaleDateString();
  } catch (e) {
    console.error("Error formatting date:", e);
    return dateTimeString; // Return original string if formatting fails
  }
};

export const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'Unknown date';
  try {
    // Format to locale date string (e.g., '12/31/2023')
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    console.error("Error formatting date:", e);
    return dateString; // Return original string if formatting fails
  }
};

// You can add more specific formatting functions if needed 