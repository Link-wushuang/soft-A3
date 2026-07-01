export function createSSE(url: string, onEvent: (event: MessageEvent) => void, onDone?: () => void) {
  const token = localStorage.getItem('token')
  const fullUrl = url.includes('?') ? `${url}&token=${token}` : `${url}?token=${token}`
  const source = new EventSource(fullUrl)

  source.addEventListener('agent_status', onEvent)
  source.addEventListener('resource_ready', onEvent)
  source.addEventListener('profile_ready', onEvent)
  source.addEventListener('token', onEvent)
  source.addEventListener('done', (e) => {
    onEvent(e)
    source.close()
    onDone?.()
  })
  source.addEventListener('error', () => {
    source.close()
    onDone?.()
  })

  return source
}
