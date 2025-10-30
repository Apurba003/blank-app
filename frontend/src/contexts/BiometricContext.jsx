import React, { createContext, useState, useContext } from 'react';

const BiometricContext = createContext(null);

export const useBiometric = () => {
  const context = useContext(BiometricContext);
  if (!context) {
    throw new Error('useBiometric must be used within a BiometricProvider');
  }
  return context;
};

export const BiometricProvider = ({ children }) => {
  const [keystrokeData, setKeystrokeData] = useState([]);
  const [faceImage, setFaceImage] = useState(null);
  const [enrollmentProgress, setEnrollmentProgress] = useState({
    keystroke: false,
    face: false,
  });

  const clearKeystrokeData = () => setKeystrokeData([]);
  const clearFaceImage = () => setFaceImage(null);
  const clearAll = () => {
    clearKeystrokeData();
    clearFaceImage();
  };

  const updateEnrollmentProgress = (modality, status) => {
    setEnrollmentProgress((prev) => ({
      ...prev,
      [modality]: status,
    }));
  };

  const value = {
    keystrokeData,
    setKeystrokeData,
    faceImage,
    setFaceImage,
    enrollmentProgress,
    updateEnrollmentProgress,
    clearKeystrokeData,
    clearFaceImage,
    clearAll,
  };

  return (
    <BiometricContext.Provider value={value}>
      {children}
    </BiometricContext.Provider>
  );
};
