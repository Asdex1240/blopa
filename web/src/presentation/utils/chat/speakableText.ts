export function speakableText(text: string) {
  return text
    .replace(/https?:\/\/\S+/g, "")
    .replace(/[*_#`>|~[\]()]/g, "")
    .replace(/\p{Extended_Pictographic}/gu, "")
    .replace(/°C/g, " grados")
    .replace(/\s+/g, " ")
    .trim()
}
