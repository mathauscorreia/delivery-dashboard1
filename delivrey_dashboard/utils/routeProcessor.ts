/**
 * Design: Eficiência Cromática Dinâmica
 * Core logic for SPX route processing and stop grouping
 */

export interface SPXStop {
  endereco: string;
  numero: string;
  complemento: string;
  bairro: string;
  id: string;
  ordem: number;
  sequence?: string | number; // Package sequence number from SPX file
}

export interface GroupedStop {
  name: string;
  addressLine1: string;
  addressLine2: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  notes: string;
  packageCount: number;
  packageIds: string[];
  originalAddresses: string[];
}

export interface ProcessingResult {
  originalCount: number;
  groupedCount: number;
  reductionPercentage: number;
  groupedStops: GroupedStop[];
}

/**
 * Normalize text for comparison:
 * - Convert to lowercase
 * - Remove accents
 * - Normalize street type abbreviations
 * - Remove extra spaces
 */
export function normalizeText(text: string | null | undefined): string {
  if (!text) return '';
  
  let normalized = text.toLowerCase().trim();
  
  // Remove accents
  normalized = normalized.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  
  // Normalize street types
  const streetTypes: Record<string, string> = {
    'rua': 'r',
    'r.': 'r',
    'avenida': 'av',
    'av.': 'av',
    'travessa': 'tv',
    'tv.': 'tv',
    'praca': 'pc',
    'pc.': 'pc',
    'alameda': 'al',
    'al.': 'al',
  };
  
  // Replace street types at the beginning of the string
  for (const [full, abbr] of Object.entries(streetTypes)) {
    const regex = new RegExp(`^${full}\\s+`, 'i');
    normalized = normalized.replace(regex, `${abbr} `);
  }
  
  // Remove extra spaces
  normalized = normalized.replace(/\s+/g, ' ').trim();
  
  return normalized;
}

/**
 * Create a unique key for grouping stops
 * Groups by: endereco + numero + bairro (ignores complemento)
 * This way, different apartments/units at the same address are grouped together
 */
export function createStopKey(stop: SPXStop): string {
  const endereco = normalizeText(stop.endereco);
  const numero = normalizeText(stop.numero);
  const bairro = normalizeText(stop.bairro);
  
  // Group by street + number + neighborhood (ignore complemento/apartment)
  return `${endereco}|${numero}|${bairro}`;
}

/**
 * Group stops by address
 */
export function groupStops(stops: SPXStop[]): Map<string, SPXStop[]> {
  const grouped = new Map<string, SPXStop[]>();
  
  for (const stop of stops) {
    const key = createStopKey(stop);
    
    if (!grouped.has(key)) {
      grouped.set(key, []);
    }
    
    grouped.get(key)!.push(stop);
  }
  
  return grouped;
}

/**
 * Convert grouped stops to Spoke-compatible format
 */
export function convertToSpokeFormat(groupedMap: Map<string, SPXStop[]>): GroupedStop[] {
  const result: GroupedStop[] = [];
  
  for (const [, stops] of Array.from(groupedMap)) {
    const firstStop = stops[0];
    const packageIds = stops.map((s: SPXStop) => s.id).filter(Boolean);
    const packageCount = stops.length;
    
    // Build address line 1: street + number
    const addressLine1 = `${firstStop.endereco}${firstStop.numero ? ', ' + firstStop.numero : ''}`;
    
    // Build notes with sequence numbers (package numbers) instead of IDs
      const sequenceNumbers = stops
        .map((s) => {
          const seq = s.sequence;

          if (
            seq !== undefined &&
            seq !== null &&
            String(seq).trim() !== "" &&
            String(seq).trim() !== "-"
          ) {
            return String(seq).trim();
          }

          // fallback para ID caso sequence esteja vazio
          return s.id ? String(s.id).trim() : null;
        })
        .filter((seq) => seq !== null);

    
    const notes = sequenceNumbers.length > 0 
      ? sequenceNumbers.join(', ')
      : `${packageCount} pacote${packageCount > 1 ? 's' : ''}`;
    
    const groupedStop: GroupedStop = {
      name: addressLine1,
      addressLine1: addressLine1,
      addressLine2: firstStop.complemento || '',
      city: 'Recife',
      state: 'PE',
      postalCode: '',
      country: 'Brasil',
      notes: notes,
      packageCount: packageCount,
      packageIds: packageIds,
      originalAddresses: stops.map((s: SPXStop) => 
        `${s.endereco}, ${s.numero}${s.complemento ? ' - ' + s.complemento : ''}, ${s.bairro}`
      ),
    };
    
    result.push(groupedStop);
  }
  
  // Sort by package count (descending) for better visualization
  result.sort((a, b) => b.packageCount - a.packageCount);
  
  return result;
}

/**
 * Main processing function
 */
export function processRoute(stops: SPXStop[]): ProcessingResult {
  const originalCount = stops.length;
  
  // Group stops by normalized address
  const groupedMap = groupStops(stops);
  
  // Convert to Spoke format
  const groupedStops = convertToSpokeFormat(groupedMap);
  
  const groupedCount = groupedStops.length;
  const reductionPercentage = originalCount > 0 
    ? Math.round(((originalCount - groupedCount) / originalCount) * 100)
    : 0;
  
  return {
    originalCount,
    groupedCount,
    reductionPercentage,
    groupedStops,
  };
}
