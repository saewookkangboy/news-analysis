import React from 'react';
import type { CategoryType } from '../services/dashboardService';

interface CategorySelectorProps {
  selectedCategory?: CategoryType;
  onCategoryChange?: (category: CategoryType) => void;
}

const CategorySelector: React.FC<CategorySelectorProps> = () => {
  return null;
};

export default CategorySelector;
