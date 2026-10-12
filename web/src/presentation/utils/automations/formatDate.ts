const formatter = new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" })

export const formatDate = (iso: string) => formatter.format(new Date(iso))
