/**
 * Excel export utilities for Spoke-compatible format (React Native compatible)
 */

import * as XLSX from 'xlsx';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import type { GroupedStop } from './routeProcessor';

/**
 * Helper function to generate and share XLSX file
 */
async function generateAndShareFile(
  workbook: XLSX.WorkBook,
  filename: string
): Promise<void> {

  const base64 = XLSX.write(workbook, {
    type: 'base64',
    bookType: 'xlsx',
  });

  const fileUri = FileSystem.documentDirectory + filename;

  await FileSystem.writeAsStringAsync(fileUri, base64, {
    encoding: FileSystem.EncodingType.Base64,
  });

  await Sharing.shareAsync(fileUri);
}


/**
 * Export grouped stops to Spoke-compatible XLSX file
 */
export async function exportToSpoke(
  groupedStops: GroupedStop[],
  filename: string = 'rota_spoke.xlsx'
): Promise<void> {
  const worksheetData = [
  [
    'Name',
    'Address Line 1',
    'Address Line 2',
    'City',
    'State',
    'Postal Code',
    'Country',
    'Latitude',
    'Longitude',
    'Notes',
  ],

  ...groupedStops.map(stop => [
    stop.name,
    stop.addressLine1,
    stop.addressLine2,
    stop.city,
    stop.state,
    stop.postalCode,
    stop.country,
    stop.latitude,
    stop.longitude,
    stop.notes,
  ]),
  ];

  const workbook = XLSX.utils.book_new();
  const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

  worksheet['!cols'] = [
    { wch: 40 },
    { wch: 40 },
    { wch: 25 },
    { wch: 15 },
    { wch: 8 },
    { wch: 12 },
    { wch: 10 },
    { wch: 50 },
  ];

  XLSX.utils.book_append_sheet(workbook, worksheet, 'Rotas Agrupadas');

  await generateAndShareFile(workbook, filename);
}

/**
 * Export detailed report with statistics
 */
export async function exportDetailedReport(
  groupedStops: GroupedStop[],
  originalCount: number,
  groupedCount: number,
  reductionPercentage: number,
  filename: string = 'relatorio_completo.xlsx'
): Promise<void> {

  const workbook = XLSX.utils.book_new();

  // Estatísticas
  const statsData = [
    ['Relatório de Agrupamento de Rotas SPX'],
    [''],
    ['Estatísticas'],
    ['Total de paradas originais', originalCount],
    ['Total de paradas agrupadas', groupedCount],
    ['Paradas eliminadas', originalCount - groupedCount],
    ['Redução percentual', `${reductionPercentage}%`],
    [''],
    ['Gerado em', new Date().toLocaleString('pt-BR')],
  ];

  const statsSheet = XLSX.utils.aoa_to_sheet(statsData);
  statsSheet['!cols'] = [{ wch: 30 }, { wch: 20 }];
  XLSX.utils.book_append_sheet(workbook, statsSheet, 'Estatísticas');

  // Formato Spoke
  const spokeData = [
    [
      'Name',
      'Address Line 1',
      'Address Line 2',
      'City',
      'State',
      'Postal Code',
      'Country',
      'Latitude',
      'Longitude',
      'Notes',
    ],

    ...groupedStops.map(stop => [
      stop.name,
      stop.addressLine1,
      stop.addressLine2,
      stop.city,
      stop.state,
      stop.postalCode,
      stop.country,
      stop.latitude,
      stop.longitude,
      stop.notes,
    ]),

  ];

  const spokeSheet = XLSX.utils.aoa_to_sheet(spokeData);
  XLSX.utils.book_append_sheet(workbook, spokeSheet, 'Formato Spoke');

  // Detalhamento
  const detailedData = [
    [
      'Endereço Completo',
      'Complemento',
      'Bairro',
      'Qtd Pacotes',
      'IDs dos Pacotes',
    ],
    ...groupedStops.map(stop => [
      stop.addressLine1,
      stop.addressLine2,
      stop.city,
      stop.packageCount,
      stop.packageIds.join(', '),
    ]),
  ];

  const detailedSheet = XLSX.utils.aoa_to_sheet(detailedData);
  XLSX.utils.book_append_sheet(workbook, detailedSheet, 'Detalhamento');

  await generateAndShareFile(workbook, filename);
}
