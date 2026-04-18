function sanitize(value) {
  return String(value ?? '').replace(/[^\x20-\x7E]/g, ' ')
}

function escapePdfText(value) {
  return sanitize(value).replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)')
}

function humanizeMetricKey(key) {
  return String(key)
    .replace(/([A-Z])/g, ' $1')
    .replace(/[_-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^./, (char) => char.toUpperCase())
}

function buildReportLines(report) {
  const lines = [
    'SONIK BUSINESS REPORT',
    '',
    `Report: ${report?.name || 'Business Report'}`,
    `Type: ${(report?.type || 'general').toUpperCase()}`,
    `Date: ${report?.date || '-'}`,
    `Generated At: ${report?.generatedAt || '-'}`,
    `Status: ${(report?.status || 'completed').toUpperCase()}`,
    '',
    'Key Metrics',
  ]

  Object.entries(report?.metrics || {}).forEach(([key, value]) => {
    lines.push(`${humanizeMetricKey(key)}: ${sanitize(value)}`)
  })

  lines.push('', 'Generated from Sonik reports dashboard.')
  return lines
}

export function downloadBusinessReportPdf(report) {
  const lines = buildReportLines(report)
  const streamLines = ['BT', '/F1 12 Tf', '40 800 Td']

  lines.forEach((line, index) => {
    if (index === 0) {
      streamLines.push(`(${escapePdfText(line)}) Tj`)
    } else {
      streamLines.push('0 -18 Td')
      streamLines.push(`(${escapePdfText(line)}) Tj`)
    }
  })

  streamLines.push('ET')
  const contentStream = `${streamLines.join('\n')}\n`

  const objects = []
  const addObject = (value) => {
    objects.push(value)
    return objects.length
  }

  const fontId = addObject('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
  const contentId = addObject(`<< /Length ${contentStream.length} >>\nstream\n${contentStream}endstream`)
  const pageId = addObject(
    `<< /Type /Page /Parent 4 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 ${fontId} 0 R >> >> /Contents ${contentId} 0 R >>`,
  )
  const pagesId = addObject(`<< /Type /Pages /Kids [${pageId} 0 R] /Count 1 >>`)
  const catalogId = addObject(`<< /Type /Catalog /Pages ${pagesId} 0 R >>`)

  let pdf = '%PDF-1.4\n'
  const offsets = [0]

  objects.forEach((object, index) => {
    offsets.push(pdf.length)
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`
  })

  const xrefOffset = pdf.length
  pdf += `xref\n0 ${objects.length + 1}\n`
  pdf += '0000000000 65535 f \n'
  offsets.slice(1).forEach((offset) => {
    pdf += `${String(offset).padStart(10, '0')} 00000 n \n`
  })
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root ${catalogId} 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`

  const blob = new Blob([pdf], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const filename = sanitize(report?.name || 'business-report').replace(/\s+/g, '-').toLowerCase()
  link.href = url
  link.download = `${filename}.pdf`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}
