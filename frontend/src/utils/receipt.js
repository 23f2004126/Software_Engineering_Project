import { formatCurrency } from './currency.js'

function sanitize(value) {
  return String(value ?? '').replace(/[^\x20-\x7E]/g, ' ')
}

function escapePdfText(value) {
  return sanitize(value).replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)')
}

function buildReceiptLines(sale) {
  const items = sale?.items || []
  const customerName = sale?.customer?.name || 'Walk-in Customer'
  const lines = [
    'SONIK GENERAL STORE',
    'Tax Invoice',
    '',
    `Receipt: ${sale?.receipt_number || '-'}`,
    `Date: ${new Date(sale?.bill_date || Date.now()).toLocaleString('en-IN')}`,
    `Customer: ${customerName}`,
    `Payment: ${(sale?.payment_method || 'cash').toUpperCase()}`,
    sale?.payment_details?.payment_id ? `Payment ID: ${sale.payment_details.payment_id}` : '',
    '',
    'Items',
  ]

  items.forEach((item, index) => {
    const productName = item.product?.name || item.name || `Item ${index + 1}`
    lines.push(
      `${index + 1}. ${productName}`,
      `   ${item.quantity} x ${formatCurrency(item.unit_price)} = ${formatCurrency(item.subtotal)}`,
    )
  })

  lines.push(
    '',
    `Tax: ${formatCurrency(sale?.tax_amount || 0)}`,
    `Discount: ${formatCurrency(sale?.discount_amount || 0)}`,
    `Total: ${formatCurrency(sale?.total_amount || 0)}`,
    '',
    'Thank you for your business.',
  )

  return lines.filter((line, index, arr) => line || arr[index - 1] !== '')
}

export function downloadSaleReceiptPdf(sale) {
  const lines = buildReceiptLines(sale)
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
  link.href = url
  link.download = `${sale?.receipt_number || 'receipt'}.pdf`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function buildPrintableHtml(sale) {
  const rows = (sale?.items || [])
    .map((item, index) => {
      const productName = sanitize(item.product?.name || item.name || `Item ${index + 1}`)
      return `
        <tr>
          <td>${index + 1}</td>
          <td>${productName}</td>
          <td>${item.quantity}</td>
          <td>${sanitize(formatCurrency(item.unit_price))}</td>
          <td>${sanitize(formatCurrency(item.subtotal))}</td>
        </tr>
      `
    })
    .join('')

  return `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>${sanitize(sale?.receipt_number || 'Receipt')}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 24px; color: #0f172a; }
          h1, h2, p { margin: 0 0 8px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th, td { border-bottom: 1px solid #cbd5e1; padding: 10px 8px; text-align: left; }
          .meta { margin-top: 16px; }
          .totals { margin-top: 20px; width: 320px; margin-left: auto; }
          .totals div { display: flex; justify-content: space-between; padding: 4px 0; }
          .total { font-weight: bold; font-size: 18px; }
        </style>
      </head>
      <body>
        <h1>SONIK GENERAL STORE</h1>
        <h2>Tax Invoice</h2>
        <div class="meta">
          <p>Receipt: ${sanitize(sale?.receipt_number || '-')}</p>
          <p>Date: ${sanitize(new Date(sale?.bill_date || Date.now()).toLocaleString('en-IN'))}</p>
          <p>Customer: ${sanitize(sale?.customer?.name || 'Walk-in Customer')}</p>
          <p>Payment: ${sanitize((sale?.payment_method || 'cash').toUpperCase())}</p>
        </div>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Product</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
        <div class="totals">
          <div><span>Tax</span><span>${sanitize(formatCurrency(sale?.tax_amount || 0))}</span></div>
          <div><span>Discount</span><span>${sanitize(formatCurrency(sale?.discount_amount || 0))}</span></div>
          <div class="total"><span>Total</span><span>${sanitize(formatCurrency(sale?.total_amount || 0))}</span></div>
        </div>
      </body>
    </html>
  `
}

export function openSalePrintView(sale) {
  const printWindow = window.open('', '_blank', 'width=900,height=700')

  if (!printWindow) {
    throw new Error('Unable to open print window')
  }

  printWindow.document.write(buildPrintableHtml(sale))
  printWindow.document.close()
  printWindow.focus()
  printWindow.print()
}
