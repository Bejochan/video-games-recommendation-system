export async function testBackend() {
  const response = await fetch('http://127.0.0.1:5000/');
  const text = await response.text();
  return text;
}