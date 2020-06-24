export const saveProgram = async ({ id, name, program_type, attrs }, steps) => {
  let url = `http://${location.host}/api/programs`;
  if (id) url += `/${id}`;
  const method = id ? "put" : "post";
  return await fetch(url, {
    method: method,
    header: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id,
      name,
      program_type,
      attrs,
      steps,
    }),
  });
};
