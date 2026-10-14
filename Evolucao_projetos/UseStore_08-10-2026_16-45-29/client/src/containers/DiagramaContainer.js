import React, { useState, useEffect } from "react";
import Diagrama from "./components/Diagrama";

const DiagramaContainer = () => {
  const [diagrama, setDiagrama] = useState(null);

  useEffect(() => {
    fetch("/api/diagramas")
      .then(response => response.json())
      .then(data => setDiagrama(data));
  }, []);

  return (
    <div>
      <Diagrama diagrama={diagrama} />
    </div>
  );
};

export default DiagramaContainer;