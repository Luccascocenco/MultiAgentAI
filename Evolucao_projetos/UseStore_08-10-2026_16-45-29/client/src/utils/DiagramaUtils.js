export const getDiagramaById = (id) => {
  return fetch(`/api/diagramas/${id}`)
    .then(response => response.json())
    .then(diagrama => diagrama);
};