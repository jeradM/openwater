export const saveZone = async ({
  id,
  name,
  zone_type,
  is_master,
  open_offset,
  close_offset,
  attrs,
}) => {
  debugger;
  const _is_master = !!is_master;
  let url = `http:///${location.host}/api/zones`;
  if (id) url += `/${id}`;
  const method = id ? "put" : "post";
  console.log("is_master", is_master);
  return await fetch(url, {
    method: method,
    header: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id,
      name,
      zone_type,
      is_master: _is_master,
      open_offset,
      close_offset,
      attrs,
    }),
  });
};

export const deleteZone = async ({ id }) => {
  const url = `http://localhost:8000/api/zones/${id}`;
  return await fetch(url, {
    method: "delete",
  });
};
// export const sendZoneCmd = async (id, cmd) => {};
