/**
 * Column Filtering Utilities
 * 
 * Utilities for filtering table columns based on printer capabilities
 */

import type { 
  ColumnDefinition, 
  ColumnVisibilityConfig,
  ColumnGroup 
} from '../types/printer';
import { shouldShowColumn, shouldShowGroupHeader } from '../types/printer';

/**
 * Filter columns based on visibility configuration
 * 
 * @param columns - Array of column definitions
 * @param visibility - Column visibility configuration
 * @returns Filtered array of visible columns
 * 
 * @example
 * ```tsx
 * const allColumns: ColumnDefinition[] = [
 *   { key: 'usuario', label: 'Usuario', group: 'basic' },
 *   { key: 'color', label: 'Color', group: 'color' },
 * ];
 * 
 * const visibleColumns = filterColumns(allColumns, visibility);
 * ```
 */
export function filterColumns(
  columns: ColumnDefinition[],
  visibility: ColumnVisibilityConfig
): ColumnDefinition[] {
  return columns.filter(column => {
    // Always show columns marked as alwaysVisible
    if (column.alwaysVisible) {
      return true;
    }
    
    // Check visibility based on group
    return shouldShowColumn(column.group, visibility);
  });
}

/**
 * Check if a specific column should be shown
 * 
 * @param column - Column definition
 * @param visibility - Column visibility configuration
 * @returns Whether the column should be visible
 * 
 * @example
 * ```tsx
 * const column = { key: 'color', label: 'Color', group: 'color' };
 * const isVisible = shouldShowColumnDef(column, visibility);
 * ```
 */
export function shouldShowColumnDef(
  column: ColumnDefinition,
  visibility: ColumnVisibilityConfig
): boolean {
  if (column.alwaysVisible) {
    return true;
  }
  
  return shouldShowColumn(column.group, visibility);
}

/**
 * Group columns by their group property
 * 
 * @param columns - Array of column definitions
 * @returns Map of group to columns
 * 
 * @example
 * ```tsx
 * const grouped = groupColumns(columns);
 * const colorColumns = grouped.get('color') || [];
 * ```
 */
export function groupColumns(
  columns: ColumnDefinition[]
): Map<ColumnGroup, ColumnDefinition[]> {
  const grouped = new Map<ColumnGroup, ColumnDefinition[]>();
  
  for (const column of columns) {
    const group = column.group;
    if (!grouped.has(group)) {
      grouped.set(group, []);
    }
    grouped.get(group)!.push(column);
  }
  
  return grouped;
}

/**
 * Get visible columns grouped by their group
 * 
 * @param columns - Array of column definitions
 * @param visibility - Column visibility configuration
 * @returns Map of group to visible columns
 * 
 * @example
 * ```tsx
 * const visibleGrouped = getVisibleColumnsByGroup(columns, visibility);
 * ```
 */
export function getVisibleColumnsByGroup(
  columns: ColumnDefinition[],
  visibility: ColumnVisibilityConfig
): Map<ColumnGroup, ColumnDefinition[]> {
  const visibleColumns = filterColumns(columns, visibility);
  return groupColumns(visibleColumns);
}

/**
 * Check if any column in a group is visible
 * 
 * @param group - Column group
 * @param columns - Array of column definitions
 * @param visibility - Column visibility configuration
 * @returns Whether any column in the group is visible
 * 
 * @example
 * ```tsx
 * const hasVisibleColorColumns = hasVisibleColumnsInGroup('color', columns, visibility);
 * ```
 */
export function hasVisibleColumnsInGroup(
  group: ColumnGroup,
  columns: ColumnDefinition[],
  visibility: ColumnVisibilityConfig
): boolean {
  const groupColumns = columns.filter(col => col.group === group);
  return groupColumns.some(col => shouldShowColumnDef(col, visibility));
}

/**
 * Get column count for a group
 * 
 * @param group - Column group
 * @param columns - Array of column definitions
 * @param visibility - Column visibility configuration
 * @returns Number of visible columns in the group
 * 
 * @example
 * ```tsx
 * const colorColumnCount = getVisibleColumnCount('color', columns, visibility);
 * ```
 */
export function getVisibleColumnCount(
  group: ColumnGroup,
  columns: ColumnDefinition[],
  visibility: ColumnVisibilityConfig
): number {
  const groupColumns = columns.filter(col => col.group === group);
  return groupColumns.filter(col => shouldShowColumnDef(col, visibility)).length;
}

/**
 * Create column span for group headers
 * 
 * @param group - Column group
 * @param columns - Array of column definitions
 * @param visibility - Column visibility configuration
 * @returns Column span value for the group header
 * 
 * @example
 * ```tsx
 * <th colSpan={getGroupHeaderColSpan('color', columns, visibility)}>
 *   Color
 * </th>
 * ```
 */
export function getGroupHeaderColSpan(
  group: ColumnGroup,
  columns: ColumnDefinition[],
  visibility: ColumnVisibilityConfig
): number {
  return getVisibleColumnCount(group, columns, visibility);
}

/**
 * Check if a group header should be rendered
 * 
 * @param group - Column group
 * @param columns - Array of column definitions
 * @param visibility - Column visibility configuration
 * @returns Whether the group header should be rendered
 * 
 * @example
 * ```tsx
 * {shouldRenderGroupHeader('color', columns, visibility) && (
 *   <th colSpan={getGroupHeaderColSpan('color', columns, visibility)}>
 *     Color
 *   </th>
 * )}
 * ```
 */
export function shouldRenderGroupHeader(
  group: ColumnGroup,
  columns: ColumnDefinition[],
  visibility: ColumnVisibilityConfig
): boolean {
  // Don't render header for basic group
  if (group === 'basic') {
    return false;
  }
  
  // Check if group should be shown and has visible columns
  return shouldShowGroupHeader(group, visibility) && 
         hasVisibleColumnsInGroup(group, columns, visibility);
}
