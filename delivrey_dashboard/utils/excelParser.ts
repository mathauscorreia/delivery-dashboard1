/**
 * Design: Eficiência Cromática Dinâmica
 * Excel file parsing utilities for SPX XLSX files
 * Supports both manual format and SPX export format
 */

import * as XLSX from 'xlsx';
import type { SPXStop } from './routeProcessor';

export interface ParseError {
  message: string;
  details?: string;
}

/**
 * Parse SPX XLSX file and extract stop data
 */
export async function parseXLSXFile(file: File): Promise<SPXStop[]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const data = e.target?.result;
        if (!data) {
          reject({ message: 'Erro ao ler arquivo', details: 'Dados vazios' });
          return;
        }
        
        // Parse workbook
        const workbook = XLSX.read(data, { type: 'binary' });
        
        // Get first sheet
        const firstSheetName = workbook.SheetNames[0];
        if (!firstSheetName) {
          reject({ message: 'Arquivo vazio', details: 'Nenhuma planilha encontrada' });
          return;
        }
        
        const worksheet = workbook.Sheets[firstSheetName];
        
        // Convert to JSON
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { 
          header: 1,
          defval: '',
        }) as string[][];
        
        if (jsonData.length < 2) {
          reject({ message: 'Arquivo inválido', details: 'Planilha não contém dados' });
          return;
        }
        
        // Parse header and data
        const stops = parseSheetData(jsonData);
        
        if (stops.length === 0) {
          reject({ message: 'Nenhuma parada encontrada', details: 'Verifique o formato do arquivo' });
          return;
        }
        
        resolve(stops);
      } catch (error) {
        reject({ 
          message: 'Erro ao processar arquivo', 
          details: error instanceof Error ? error.message : 'Erro desconhecido' 
        });
      }
    };
    
    reader.onerror = () => {
      reject({ message: 'Erro ao ler arquivo', details: 'Falha na leitura do arquivo' });
    };
    
    reader.readAsBinaryString(file);
  });
}

/**
 * Parse sheet data and map to SPXStop objects
 * Supports both manual format and SPX export format
 */
function parseSheetData(data: string[][]): SPXStop[] {
  const header = data[0].map((h: string) => normalizeHeader(h));
  const rows = data.slice(1);
  
  // Find column indices - try both formats
  const indices = {
    endereco: findColumnIndex(header, ['endereco', 'endereco', 'logradouro', 'rua', 'destinationaddress']),
    numero: findColumnIndex(header, ['numero', 'numero', 'num', 'nro']),
    complemento: findColumnIndex(header, ['complemento', 'compl', 'comp']),
    bairro: findColumnIndex(header, ['bairro', 'distrito']),
    id: findColumnIndex(header, ['id', 'codigo', 'codigo', 'encomenda', 'pacote', 'spxtn', 'tn']),
    ordem: findColumnIndex(header, ['ordem', 'order', 'sequencia', 'sequencia', 'sequence', 'stop']),
    sequence: findColumnIndex(header, ['sequence', 'sequencia', 'seq']),
  };
  
  // Validate required columns
  if (indices.endereco === -1) {
    throw new Error('Coluna de endereco nao encontrada');
  }
  
  const stops: SPXStop[] = [];
  
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    
    // Skip empty rows
    if (!row || row.every((cell: string) => !cell)) {
      continue;
    }
    
    let endereco = getCellValue(row, indices.endereco);
    let numero = getCellValue(row, indices.numero);
    let complemento = getCellValue(row, indices.complemento);
    
    // If endereco contains the full address (SPX format), parse it
    if (endereco && !numero) {
      const parsed = parseFullAddress(endereco);
      endereco = parsed.endereco;
      numero = parsed.numero;
      complemento = parsed.complemento;
    }
    
    const stop: SPXStop = {
      endereco: endereco,
      numero: numero,
      complemento: complemento,
      bairro: getCellValue(row, indices.bairro),
      id: getCellValue(row, indices.id) || `PKG-${i + 1}`,
      ordem: indices.ordem !== -1 ? parseInt(getCellValue(row, indices.ordem)) || (i + 1) : (i + 1),
      sequence: indices.sequence !== -1 ? getCellValue(row, indices.sequence) : undefined,
    };
    
    // Only add stops with valid address
    if (stop.endereco) {
      stops.push(stop);
    }
  }
  
  return stops;
}

/**
 * Normalize header text for comparison
 */
function normalizeHeader(header: string): string {
  return header
    .toLowerCase()
    .trim()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, '');
}

/**
 * Find column index by possible header names
 */
function findColumnIndex(headers: string[], possibleNames: string[]): number {
  const normalizedNames = possibleNames.map(normalizeHeader);
  
  for (let i = 0; i < headers.length; i++) {
    if (normalizedNames.includes(headers[i])) {
      return i;
    }
  }
  
  return -1;
}

/**
 * Get cell value safely
 */
function getCellValue(row: string[], index: number): string {
  if (index === -1 || index >= row.length) {
    return '';
  }
  
  const value = row[index];
  return value ? String(value).trim() : '';
}

/**
 * Parse full address string from SPX format
 * Intelligently extracts street, number, and complement from various formats
 * 
 * Examples:
 * - "Rua X, 123, Apartamento 301" -> street: "Rua X", number: "123", complement: "Apartamento 301"
 * - "Rua X, Apartamento 301" -> street: "Rua X", number: "301", complement: "Apartamento 301"
 * - "Rua X, 123" -> street: "Rua X", number: "123", complement: ""
 */
function parseFullAddress(fullAddress: string): { endereco: string; numero: string; complemento: string } {
  // Remove city and state if present
  let address = fullAddress;
  
  // Remove common city/state patterns at the end
  address = address.replace(/,\s*Recife\s*,\s*Pernambuco.*$/i, '');
  address = address.replace(/,\s*Recife.*$/i, '');
  address = address.trim();
  
  // Split by comma
  const parts = address.split(',').map(p => p.trim());
  
  if (parts.length === 0) {
    return { endereco: fullAddress, numero: '', complemento: '' };
  }
  
  // First part is always the street
  const endereco = parts[0];
  
  // Try to find the number in the remaining parts
  let numero = '';
  let complemento = '';
  
  // First pass: look for a part that starts with a number (e.g., "123" or "123 Apt")
  for (let i = 1; i < parts.length; i++) {
    const part = parts[i];
    const numberMatch = part.match(/^(\d+)/);
    if (numberMatch) {
      numero = numberMatch[1];
      // Rest is complemento
      const rest = part.substring(numero.length).trim();
      if (rest) {
        complemento = rest;
      }
      // Join remaining parts as complemento
      if (i + 1 < parts.length) {
        const remaining = parts.slice(i + 1).join(', ');
        complemento = complemento ? `${complemento}, ${remaining}` : remaining;
      }
      return { endereco, numero, complemento };
    }
  }
  
  // Second pass: if no number found yet, look for numbers within complemento parts
  // This handles cases like "Apartamento 301", "Apto 301", "Casa A 123", etc.
  if (!numero && parts.length > 1) {
    // Join all remaining parts
    const allRest = parts.slice(1).join(', ');
    complemento = allRest;
    
    // Look for patterns like "Apartamento 301", "Apto 301", "Casa 123", "Bloco A 301", etc.
    // Match: optional prefix (Apartamento, Apto, Casa, etc.) + optional letter + number
    const patterns = [
      /(?:Apartamento|Apto|Apt|Ap)\s+([A-Z]?\s*)?(\d+)/i,  // Apartamento 301 or Apto A 301
      /(?:Casa|Bloco|Bl|Loja|Sala|Lote)\s+([A-Z]?\s*)?(\d+)/i,  // Casa 123 or Bloco A 301
      /(\d+)\s+(?:Apartamento|Apto|Apt|Ap|Casa|Bloco|Bl|Loja|Sala|Lote)/i,  // 301 Apartamento
      /\b(\d+)\b/,  // Any standalone number
    ];
    
    for (const pattern of patterns) {
      const match = allRest.match(pattern);
      if (match) {
        // Find the number in the match groups
        for (let j = match.length - 1; j > 0; j--) {
          if (match[j] && /^\d+$/.test(match[j])) {
            numero = match[j];
            break;
          }
        }
        if (numero) break;
      }
    }
  }
  
  return { endereco, numero, complemento };
}


/**
 * React Native version - parse from base64
 */
export function parseXLSXBase64(base64: string) {
  try {
    // RN precisa type: 'base64'
    const workbook = XLSX.read(base64, { type: "base64" });

    const firstSheetName = workbook.SheetNames[0];
    if (!firstSheetName) {
      throw new Error("Nenhuma planilha encontrada");
    }

    const worksheet = workbook.Sheets[firstSheetName];

    const jsonData = XLSX.utils.sheet_to_json(worksheet, {
      header: 1,
      defval: "",
    }) as string[][];

    if (jsonData.length < 2) {
      throw new Error("Planilha não contém dados");
    }

    return parseSheetData(jsonData);
  } catch (error) {
    throw new Error(
      error instanceof Error ? error.message : "Erro ao processar XLSX"
    );
  }
}